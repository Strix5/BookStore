from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.cart.infrastructure.selectors import get_cart_with_items
from apps.orders.api.serializers import OrderSerializer
from apps.orders.interface.paginations import CustomOrdersPagination
from apps.orders.infrastructure.repositories import OrderRepository
from apps.orders.infrastructure.selectors import get_user_orders, get_user_order_detail


class OrderViewSet(viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomOrdersPagination

    def get_queryset(self):
        return get_user_orders(user_id=self.request.user.pk)

    def list(self, request: Request) -> Response:
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request: Request, pk: int = None) -> Response:
        order = self._get_order_or_404(order_id=pk)
        serializer = self.get_serializer(order)

        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="purchase", url_name="purchase")
    def purchase(self, request: Request) -> Response:
        cart = get_cart_with_items(user=request.user)

        order = OrderRepository().create_order_from_cart(
            user=request.user,
            cart=cart,
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _get_order_or_404(self, *, order_id: int):
        """
        Возвращает заказ пользователя или бросает NotFound.

        Проверка user_id внутри selector — нельзя получить чужой заказ.
        Используем selector (чтение), а не repository (запись).
        """
        order = get_user_order_detail(
            order_id=order_id,
            user_id=self.request.user.pk,
        )

        if order is None:
            raise NotFound(detail="Order not found.")

        return order