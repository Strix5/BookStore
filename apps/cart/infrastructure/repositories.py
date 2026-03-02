from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.books.infrastructure.models import Book
from apps.cart.infrastructure.models import CartItem
from apps.cart.infrastructure.selectors import (
    get_or_create_cart,
    get_cart_item,
)

User = get_user_model()


class CartRepository:

    @staticmethod
    @transaction.atomic
    def add_item(user: User, book_id: int, quantity: int = 1) -> Tuple[CartItem, bool]:
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")

        book = Book.objects.select_for_update().get(id=book_id, is_active=True)

        cart = get_or_create_cart(user)
        existing_item = get_cart_item(user, book_id)

        if existing_item:
            total_requested = existing_item.quantity + quantity
            if total_requested > book.in_stock:
                raise ValidationError(
                    f"Cannot add {quantity} more copies. "
                    f"In stock: {book.in_stock}, already in cart: {existing_item.quantity}."
                )
            existing_item.quantity = total_requested
            existing_item.save(update_fields=['quantity', 'updated_at'])
            return existing_item, False
        else:
            if quantity > book.in_stock:
                raise ValidationError(
                    f"Only {book.in_stock} copies available."
                )
            cart_item = CartItem.objects.create(
                cart=cart,
                book=book,
                quantity=quantity
            )
            return cart_item, True

    @staticmethod
    @transaction.atomic
    def update_quantity(user: User, book_id: int, quantity: int) -> Optional[CartItem]:
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")

        book = Book.objects.select_for_update().get(id=book_id, is_active=True)

        book_name = book.safe_translation_getter('name', any_language=True)

        if book.in_stock < 1:
            raise ValidationError(
                f"'{book_name}' is out of stock."
            )

        cart = get_or_create_cart(user)
        existing_item = get_cart_item(user, book_id)

        if existing_item:
            total_requested = existing_item.quantity + quantity
            if total_requested > book.in_stock:
                raise ValidationError(
                    f"Cannot add {quantity} more copies of '{book_name}'. "
                    f"In stock: {book.in_stock}, already in cart: {existing_item.quantity}."
                )
            existing_item.quantity = total_requested
            existing_item.save(update_fields=['quantity', 'updated_at'])
            return existing_item
        else:
            if quantity > book.in_stock:
                raise ValidationError(
                    f"Only {book.in_stock} copies of '{book_name}' available."
                )
            cart_item = CartItem.objects.create(
                cart=cart,
                book=book,
                quantity=quantity
            )
            return cart_item

    @staticmethod
    @transaction.atomic
    def remove_item(user: User, book_id: int) -> bool:
        cart_item = get_cart_item(user, book_id)

        if cart_item:
            cart_item.delete()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def clear_cart(user: User) -> int:
        cart = get_or_create_cart(user)
        deleted_count, _ = cart.items.all().delete()
        return deleted_count
