from drf_spectacular.utils import extend_schema
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
)
from apps.cart.interface.api_schema import (
    cart_list_schema, cart_add_schema, cart_patch_schema,
    cart_clear_schema, cart_remove_schema, cart_summary_schema,
)
from apps.cart.infrastructure.repositories import CartRepository
from apps.cart.infrastructure.selectors import (
    get_cart_with_items,
    get_cart_summary,
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

    @extend_schema(**cart_list_schema)
    def list(self, request: Request) -> Response:
        cart = get_cart_with_items(request.user)
        if not cart:
            return Response({
                'id': None,
                'items': [],
                'total_items': 0,
                'total_price': 0.0
            })

        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    @extend_schema(**cart_add_schema)
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

        item_serializer = CartItemSerializer(cart_item, context={'request': request})

        return Response(
            {
                'message': 'Item added to cart' if created else 'Quantity updated',
                'item': item_serializer.data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @extend_schema(**cart_patch_schema)
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

    @extend_schema(**cart_remove_schema)
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

    @extend_schema(**cart_clear_schema)
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

    @extend_schema(**cart_summary_schema)
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
