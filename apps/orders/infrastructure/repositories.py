from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from apps.books.infrastructure import Book
from apps.cart.infrastructure.models import Cart
from apps.orders.infrastructure.models import Order, OrderItem

User = get_user_model()


class OrderRepository:

    @transaction.atomic
    def create_order_from_cart(self, *, user: User, cart) -> Order:
        self._validate_cart_not_empty(cart)

        # Block books before working with them
        book_ids = [item.book_id for item in cart.items.all()]
        locked_books = {
            b.id: b for b in Book.objects.select_for_update().filter(id__in=book_ids)
        }

        # Check in stock count (доп. проверка)
        for item in cart.items.all():
            book = locked_books[item.book_id]
            if item.quantity > book.in_stock:
                book_name = book.safe_translation_getter('name', any_language=True) or f"Book #{book.id}"
                raise ValidationError({"detail": f"'{book_name}' has only {book.in_stock} copies left."})

        total_price = self._calculate_total(cart)

        order = Order.objects.create(
            user=user,
            total_price=total_price,
            status=Order.StatusChoices.PENDING,
        )

        self._create_order_items(order=order, cart=cart)
        self._decrement_stock(cart=cart)
        self._deactivate_cart(cart=cart)

        return order

    @staticmethod
    def _validate_cart_not_empty(cart) -> None:
        if cart is None or not cart.items.all():
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
        Cart.objects.filter(pk=cart.pk).update(is_active=False)

    @staticmethod
    def _decrement_stock(*, cart) -> None:
        for item in cart.items.all():
            Book.objects.filter(pk=item.book_id).update(
                in_stock=F("in_stock") - item.quantity
            )
