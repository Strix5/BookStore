from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.favorites.api.serializers import (
    FavoriteSerializer,
    AddToFavoritesSerializer,
    ToggleFavoriteSerializer
)
from apps.favorites.interface.api_schema import (
    favorite_list_schema, favorite_add_schema, favorite_remove_schema,
    favorite_toggle_schema, favorite_clear_schema, favorite_check_schema
)
from apps.favorites.infrastructure.repositories import FavoriteRepository
from apps.favorites.infrastructure.selectors import (
    get_user_favorites,
    is_book_in_favorites
)


class FavoriteViewSet(viewsets.ViewSet):
    """
    Endpoints:
    - GET /favorites/ - список избранного
    - POST /favorites/add/ - добавить в избранное
    - DELETE /favorites/remove/{book_id}/ - удалить из избранного
    - POST /favorites/toggle/ - переключить статус
    - DELETE /favorites/clear/ - очистить избранное
    - GET /favorites/check/{book_id}/ - проверить наличие
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(**favorite_list_schema)
    def list(self, request: Request) -> Response:
        """
        Получить список избранных книг.

        GET /api/favorites/
        Response:
        [
            {
                "id": 1,
                "book": {...},
                "created_at": "..."
            },
            ...
        ]
        """
        favorites = get_user_favorites(request.user)
        serializer = FavoriteSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(**favorite_add_schema)
    @action(detail=False, methods=['post'])
    def add(self, request: Request) -> Response:
        """
        Добавить книгу в избранное.

        POST /api/favorites/add/
        Body: {"book_id": 1}

        Response:
        - 201 Created: добавлено в избранное
        - 200 OK: уже было в избранном
        """
        serializer = AddToFavoritesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book_id = serializer.validated_data['book_id']

        favorite, created = FavoriteRepository.add_to_favorites(
            user=request.user,
            book_id=book_id
        )

        favorite_serializer = FavoriteSerializer(favorite, context={'request': request})

        return Response(
            {
                'message': 'Added to favorites' if created else 'Already in favorites',
                'favorite': favorite_serializer.data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @extend_schema(**favorite_remove_schema)
    @action(detail=False, methods=['delete'], url_path='remove/(?P<book_id>[0-9]+)')
    def remove(self, request: Request, book_id: int = None) -> Response:
        """
        Удалить книгу из избранного.

        DELETE /api/favorites/remove/5/

        Response:
        - 204 No Content: успешно удалено
        - 404 Not Found: не было в избранном
        """
        success = FavoriteRepository.remove_from_favorites(
            user=request.user,
            book_id=int(book_id)
        )

        if success:
            return Response(
                {'message': 'Removed from favorites'},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': 'Not in favorites'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(**favorite_toggle_schema)
    @action(detail=False, methods=['post'])
    def toggle(self, request: Request) -> Response:
        """
        Переключить статус избранного.

        POST /api/favorites/toggle/
        Body: {"book_id": 1}

        Response:
        - 200 OK: статус изменен
        """
        serializer = ToggleFavoriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book_id = serializer.validated_data['book_id']

        is_favorite, action_type = FavoriteRepository.toggle_favorite(
            user=request.user,
            book_id=book_id
        )

        return Response(
            {
                'message': f'Book {action_type}',
                'is_favorite': is_favorite
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(**favorite_clear_schema)
    @action(detail=False, methods=['delete'])
    def clear(self, request: Request) -> Response:
        """
        Очистить все избранное.

        DELETE /api/favorites/clear/

        Response:
        - 200 OK: избранное очищено
        """
        deleted_count = FavoriteRepository.clear_favorites(request.user)

        return Response(
            {
                'message': 'Favorites cleared',
                'deleted_count': deleted_count
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(**favorite_check_schema)
    @action(detail=False, methods=['get'], url_path='check/(?P<book_id>[0-9]+)')
    def check(self, request: Request, book_id: int = None) -> Response:
        """
        Проверить, есть ли книга в избранном.

        GET /api/favorites/check/5/

        Response:
        {
            "is_favorite": true
        }
        """
        is_favorite = is_book_in_favorites(
            user=request.user,
            book_id=int(book_id)
        )

        return Response({'is_favorite': is_favorite})
