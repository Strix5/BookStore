from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.cart.api.serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    FavoriteSerializer,
    AddToFavoritesSerializer,
    ToggleFavoriteSerializer
)
from apps.cart.interface.api_schema import (
    response_404_cart,
    response_401,
    response_400_stock,
    response_404_favorites,
    book_id_path
)
from apps.cart.infrastructure.repositories import CartRepository, FavoriteRepository
from apps.cart.infrastructure.selectors import (
    get_cart_with_items,
    get_cart_summary,
    get_user_favorites,
    is_book_in_favorites
)


class CartViewSet(viewsets.ViewSet):
    """
    Endpoints:
    - GET /cart/ - получить корзину
    - POST /cart/add/ - добавить книгу
    - PATCH /cart/update-quantity/{book_id}/ - изменить количество
    - DELETE /cart/remove/{book_id}/ - удалить книгу
    - DELETE /cart/clear/ - очистить корзину
    - GET /cart/summary/ - краткая сводка
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        summary="Получить корзину",
        description=(
                "Возвращает корзину пользователя со всеми позициями, "
                "количеством и итоговой стоимостью. "
                "Если корзина пуста или не создана — возвращает объект с пустым списком."
        ),
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description="Корзина пользователя.",
                examples=[
                    OpenApiExample(
                        name="Корзина с товарами",
                        value={
                            "id": 1,
                            "items": [
                                {
                                    "id": 3,
                                    "book": {
                                        "id": 5,
                                        "name": "Clean Code",
                                        "slug": "clean-code",
                                        "price": 500,
                                        "in_stock": 10,
                                    },
                                    "quantity": 2,
                                    "subtotal": 1000,
                                    "created_at": "2026-01-01T10:00:00Z",
                                    "updated_at": "2026-01-01T11:00:00Z",
                                }
                            ],
                            "total_items": 2,
                            "total_price": 1000,
                            "created_at": "2026-01-01T10:00:00Z",
                            "updated_at": "2026-01-01T11:00:00Z",
                        },
                    ),
                    OpenApiExample(
                        name="Пустая корзина",
                        value={
                            "id": None,
                            "items": [],
                            "total_items": 0,
                            "total_price": 0,
                        },
                    ),
                ],
            ),
            401: response_401,
        },
    )
    def list(self, request: Request) -> Response:
        cart = get_cart_with_items(request.user)

        if not cart:
            return Response({
                'id': None,
                'items': [],
                'total_items': 0,
                'total_price': 0.0
            })

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        tags=["Cart"],
        summary="Добавить книгу в корзину",
        description=(
                "Добавляет книгу в корзину. "
                "Если книга уже есть в корзине — увеличивает quantity. "
                "Проверяет: существование и активность книги, возраст 18+, наличие на складе."
        ),
        request=AddToCartSerializer,
        responses={
            201: OpenApiResponse(
                response=CartItemSerializer,
                description="Книга добавлена в корзину впервые.",
                examples=[
                    OpenApiExample(
                        name="Добавлена новая позиция",
                        value={
                            "message": "Item added to cart",
                            "item": {
                                "id": 3,
                                "book": {"id": 5, "name": "Clean Code", "price": 500},
                                "quantity": 2,
                                "subtotal": 1000,
                                "created_at": "2026-01-01T10:00:00Z",
                                "updated_at": "2026-01-01T11:00:00Z",
                            },
                        },
                    ),
                ],
            ),
            200: OpenApiResponse(
                response=CartItemSerializer,
                description="Книга уже была в корзине — quantity увеличен.",
                examples=[
                    OpenApiExample(
                        name="Количество увеличено",
                        value={
                            "message": "Quantity updated",
                            "item": {
                                "id": 3,
                                "book": {"id": 5, "name": "Clean Code", "price": 500},
                                "quantity": 4,
                                "subtotal": 2000,
                                "created_at": "2026-01-01T10:00:00Z",
                                "updated_at": "2026-01-01T11:00:00Z",
                            },
                        },
                    ),
                ],
            ),
            400: response_400_stock,
            401: response_401,
        },
    )
    @action(detail=False, methods=['post'])
    def add(self, request: Request) -> Response:
        """
        POST /api/cart/add/
        Body: {"book_id": 1, "quantity": 2}
        """
        serializer = AddToCartSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartRepository.add_item(
            user=request.user,
            book_id=book_id,
            quantity=quantity
        )

        item_serializer = CartItemSerializer(cart_item)

        return Response(
            {
                'message': 'Item added to cart' if created else 'Quantity updated',
                'item': item_serializer.data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Cart"],
        summary="Обновить количество книги в корзине",
        description=(
                "Устанавливает новое количество для позиции. "
                "quantity=0 удаляет позицию из корзины. "
                "Нельзя установить количество больше остатка на складе."
        ),
        parameters=[book_id_path],
        request=UpdateCartItemSerializer,
        responses={
            200: OpenApiResponse(
                response=CartItemSerializer,
                description="Количество обновлено.",
                examples=[
                    OpenApiExample(
                        name="Обновлено",
                        value={
                            "message": "Quantity updated",
                            "item": {
                                "id": 3,
                                "book": {"id": 5, "name": "Clean Code", "price": 500},
                                "quantity": 5,
                                "subtotal": 2500,
                                "created_at": "2026-01-01T10:00:00Z",
                                "updated_at": "2026-01-01T11:00:00Z",
                            },
                        },
                    ),
                ],
            ),
            204: OpenApiResponse(
                description="Позиция удалена из корзины (quantity=0).",
                examples=[
                    OpenApiExample(
                        name="Удалено через quantity=0",
                        value={"message": "Item removed from cart"},
                    ),
                ],
            ),
            400: response_400_stock,
            401: response_401,
            404: response_404_cart,
        },
    )
    @action(detail=False, methods=['patch'], url_path='update-quantity/(?P<book_id>[0-9]+)')
    def update_quantity(self, request: Request, book_id: int = None) -> Response:
        """
        PATCH /api/cart/update-quantity/5/
        Body: {"quantity": 3}
        """
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']

        try:
            cart_item = CartRepository.update_quantity(
                user=request.user,
                book_id=int(book_id),
                quantity=quantity
            )

            if cart_item is None:
                return Response(
                    {'message': 'Item removed from cart'},
                    status=status.HTTP_204_NO_CONTENT
                )

            item_serializer = CartItemSerializer(cart_item)
            return Response(
                {
                    'message': 'Quantity updated',
                    'item': item_serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=["Cart"],
        summary="Удалить книгу из корзины",
        description="Полностью удаляет позицию из корзины независимо от quantity.",
        parameters=[book_id_path],
        responses={
            204: OpenApiResponse(
                description="Позиция успешно удалена.",
                examples=[
                    OpenApiExample(
                        name="Удалено",
                        value={"message": "Item removed from cart"},
                    ),
                ],
            ),
            401: response_401,
            404: response_404_cart,
        },
    )
    @action(detail=False, methods=['delete'], url_path='remove/(?P<book_id>[0-9]+)')
    def remove(self, request: Request, book_id: int = None) -> Response:
        """
        DELETE /api/cart/remove/5/
        """
        success = CartRepository.remove_item(
            user=request.user,
            book_id=int(book_id)
        )

        if success:
            return Response(
                {'message': 'Item removed from cart'},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=["Cart"],
        summary="Очистить корзину",
        description=(
                "Удаляет все позиции из корзины. "
                "Сам объект Cart сохраняется. "
                "Возвращает количество удалённых позиций."
        ),
        responses={
            200: OpenApiResponse(
                description="Корзина очищена.",
                examples=[
                    OpenApiExample(
                        name="Очищена",
                        value={"message": "Cart cleared", "deleted_count": 3},
                    ),
                    OpenApiExample(
                        name="Корзина была пуста",
                        value={"message": "Cart cleared", "deleted_count": 0},
                    ),
                ],
            ),
            401: response_401,
        },
    )
    @action(detail=False, methods=['delete'])
    def clear(self, request: Request) -> Response:
        """
        DELETE /api/cart/clear/
        """
        deleted_count = CartRepository.clear_cart(request.user)

        return Response(
            {
                'message': 'Cart cleared',
                'deleted_count': deleted_count
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Cart"],
        summary="Сводка по корзине",
        description=(
                "Возвращает лёгкую сводку: количество позиций и уникальных книг. "
                "Используется для бейджа на иконке корзины. "
                "Не загружает данные книг — значительно быстрее GET /cart/."
        ),
        responses={
            200: OpenApiResponse(
                description="Сводка по корзине.",
                examples=[
                    OpenApiExample(
                        name="Сводка",
                        value={"total_items": 7, "unique_books": 3},
                    ),
                    OpenApiExample(
                        name="Пустая корзина",
                        value={"total_items": 0, "unique_books": 0},
                    ),
                ],
            ),
            401: response_401,
        },
    )
    @action(detail=False, methods=['get'])
    def summary(self, request: Request) -> Response:
        """
        GET /api/cart/summary/
        Response:
        {
            "total_items": 5,
            "unique_books": 3,
            "total_price": 1250.00
        }

        Зачем:
        - Бейдж на иконке корзины: "5 товаров"
        - Быстрый запрос без загрузки всех данных
        """
        summary = get_cart_summary(request.user)
        return Response(summary)


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

    @extend_schema(
        tags=["Favorites"],
        summary="Список избранных книг",
        description=(
                "Возвращает все книги пользователя из избранного, "
                "отсортированные по дате добавления (новые первые). "
                "Пустой массив если избранного нет."
        ),
        responses={
            200: OpenApiResponse(
                response=FavoriteSerializer(many=True),
                description="Список избранного.",
                examples=[
                    OpenApiExample(
                        name="Непустое избранное",
                        value=[
                            {
                                "id": 1,
                                "book": {
                                    "id": 5,
                                    "name": "Clean Code",
                                    "slug": "clean-code",
                                    "price": 500,
                                },
                                "created_at": "2024-01-15T10:00:00Z",
                            }
                        ],
                    ),
                    OpenApiExample(name="Пустое избранное", value=[]),
                ],
            ),
            401: response_401,
        },
    )
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
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Favorites"],
        summary="Добавить книгу в избранное",
        description=(
                "Добавляет книгу в избранное. "
                "Идемпотентен: повторный вызов с той же книгой возвращает 200 без ошибки."
        ),
        request=AddToFavoritesSerializer,
        responses={
            201: OpenApiResponse(
                response=FavoriteSerializer,
                description="Книга добавлена в избранное.",
                examples=[
                    OpenApiExample(
                        name="Добавлено",
                        value={
                            "message": "Added to favorites",
                            "favorite": {
                                "id": 1,
                                "book": {"id": 5, "name": "Clean Code", "price": 500},
                                "created_at": "2024-01-15T10:00:00Z",
                            },
                        },
                    ),
                ],
            ),
            200: OpenApiResponse(
                response=FavoriteSerializer,
                description="Книга уже была в избранном.",
                examples=[
                    OpenApiExample(
                        name="Уже в избранном",
                        value={
                            "message": "Already in favorites",
                            "favorite": {
                                "id": 1,
                                "book": {"id": 5, "name": "Clean Code", "price": 500},
                                "created_at": "2024-01-10T08:00:00Z",
                            },
                        },
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Книга не найдена или неактивна.",
                examples=[
                    OpenApiExample(
                        name="Не найдена",
                        value={"book_id": ["Book not found or inactive"]},
                    ),
                ],
            ),
            401: response_401,
        },
    )
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

        favorite_serializer = FavoriteSerializer(favorite)

        return Response(
            {
                'message': 'Added to favorites' if created else 'Already in favorites',
                'favorite': favorite_serializer.data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Favorites"],
        summary="Удалить книгу из избранного",
        description="Удаляет конкретную книгу из избранного пользователя.",
        parameters=[book_id_path],
        responses={
            204: OpenApiResponse(
                description="Книга удалена из избранного.",
                examples=[
                    OpenApiExample(
                        name="Удалено",
                        value={"message": "Removed from favorites"},
                    ),
                ],
            ),
            401: response_401,
            404: response_404_favorites,
        },
    )
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

    @extend_schema(
        tags=["Favorites"],
        summary="Переключить статус избранного",
        description=(
                "Добавляет книгу в избранное если её там нет, удаляет если есть. "
                "Удобно для кнопки «♥»: один запрос вместо check + add/remove."
        ),
        request=ToggleFavoriteSerializer,
        responses={
            200: OpenApiResponse(
                description="Статус переключён. is_favorite отражает текущее состояние.",
                examples=[
                    OpenApiExample(
                        name="Добавлено через toggle",
                        value={"message": "Book added", "is_favorite": True},
                    ),
                    OpenApiExample(
                        name="Удалено через toggle",
                        value={"message": "Book removed", "is_favorite": False},
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Книга не найдена или неактивна.",
                examples=[
                    OpenApiExample(
                        name="Не найдена",
                        value={"book_id": ["Book not found or inactive"]},
                    ),
                ],
            ),
            401: response_401,
        },
    )
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

    @extend_schema(
        tags=["Favorites"],
        summary="Очистить всё избранное",
        description="Удаляет все книги из избранного пользователя.",
        responses={
            200: OpenApiResponse(
                description="Избранное очищено.",
                examples=[
                    OpenApiExample(
                        name="Очищено",
                        value={"message": "Favorites cleared", "deleted_count": 5},
                    ),
                    OpenApiExample(
                        name="Было пустым",
                        value={"message": "Favorites cleared", "deleted_count": 0},
                    ),
                ],
            ),
            401: response_401,
        },
    )
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

    @extend_schema(
        tags=["Favorites"],
        summary="Проверить наличие книги в избранном",
        description=(
                "Быстрая булева проверка: есть ли книга в избранном. "
                "Используется для отображения статуса «♥» на карточках "
                "без загрузки всего списка избранного."
        ),
        parameters=[book_id_path],
        responses={
            200: OpenApiResponse(
                description="Результат проверки.",
                examples=[
                    OpenApiExample(name="В избранном", value={"is_favorite": True}),
                    OpenApiExample(name="Не в избранном", value={"is_favorite": False}),
                ],
            ),
            401: response_401,
        },
    )
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
