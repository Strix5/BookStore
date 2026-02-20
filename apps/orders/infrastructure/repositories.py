from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.orders.infrastructure.models import Order, OrderItem

User = get_user_model()


class OrderRepository:

    @transaction.atomic
    def create_order_from_cart(self, *, user: User, cart) -> Order:
        """
        Создаёт заказ из активной корзины пользователя.

        Вся логика покупки инкапсулирована в одном методе:
        1. Валидация корзины
        2. Подсчёт итоговой суммы
        3. Создание Order
        4. Массовое создание OrderItem
        5. Деактивация корзины

        @transaction.atomic гарантирует: если любой шаг упадёт,
        весь заказ откатится — нет риска получить пустой Order.

        Args:
            user: Аутентифицированный пользователь-покупатель
            cart: ORM-объект Cart с prefetch_related("items__book")

        Returns:
            Созданный объект Order со всеми позициями

        Raises:
            ValidationError: если корзина пуста или не найдена
        """
        self._validate_cart_not_empty(cart)

        total_price = self._calculate_total(cart)

        order = Order.objects.create(
            user=user,
            total_price=total_price,
            status=Order.StatusChoices.PENDING,
        )

        self._create_order_items(order=order, cart=cart)
        self._deactivate_cart(cart=cart)

        return order

    @staticmethod
    def _validate_cart_not_empty(cart) -> None:
        if cart is None or not cart.items.exists():
            raise ValidationError({"detail": "Cart is empty or does not exist."})

    @staticmethod
    def _calculate_total(cart):
        return sum(item.subtotal for item in cart.items.all())

    @staticmethod
    def _create_order_items(*, order: Order, cart) -> None:
        order_items = [
            OrderItem(
                order=order,
                book_id=item.book_id,
                quantity=item.quantity,
                price=item.book.price,
            )
            for item in cart.items.all()
        ]

        OrderItem.objects.bulk_create(order_items)

    @staticmethod
    def _deactivate_cart(*, cart) -> None:
        cart.__class__.objects.filter(pk=cart.pk).update(is_active=False)
