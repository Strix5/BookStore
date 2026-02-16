from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError

from apps.books.infrastructure.models import Book
from apps.cart.infrastructure.models import CartItem, Favorite
from apps.cart.infrastructure.selectors import (
    get_or_create_cart,
    get_cart_item,
    is_book_in_favorites
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


class FavoriteRepository:

    @staticmethod
    @transaction.atomic
    def add_to_favorites(user: User, book_id: int) -> Tuple[Favorite, bool]:
        """
        Добавляет книгу в избранное.

        Принципы:
        - Идемпотентность: повторный вызов не создает дубли
        - unique_together в модели предотвращает дубли на уровне БД

        Зачем get_or_create:
        - Безопасно при конкурентных запросах
        - Возвращает created для обратной связи в API

        Args:
            user: Пользователь
            book_id: ID книги

        Returns:
            Tuple[Favorite, bool]: (избранное, создано ли новое)

        Raises:
            Book.DoesNotExist: если книга не найдена
        """
        from apps.books.infrastructure.models import Book

        # Проверяем существование книги
        book = Book.objects.get(id=book_id, is_active=True)

        try:
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                book=book
            )
            return favorite, created
        except IntegrityError:
            # Если race condition - получаем существующую запись
            favorite = Favorite.objects.get(user=user, book=book)
            return favorite, False

    @staticmethod
    @transaction.atomic
    def remove_from_favorites(user: User, book_id: int) -> bool:
        """
        Удаляет книгу из избранного.

        Зачем:
        - Явное намерение: убрать из избранного
        - Возвращает bool для проверки
        - Транзакция для консистентности

        Args:
            user: Пользователь
            book_id: ID книги

        Returns:
            True если удалено, False если не было в избранном
        """
        try:
            favorite = Favorite.objects.get(
                user=user,
                book_id=book_id
            )
            favorite.delete()
            return True
        except Favorite.DoesNotExist:
            return False

    @staticmethod
    @transaction.atomic
    def toggle_favorite(user: User, book_id: int) -> Tuple[bool, str]:
        """
        Переключает статус избранного (добавить/удалить).

        Зачем:
        - Удобство для UI: одна кнопка "♥" для добавления/удаления
        - Меньше запросов: не нужно сначала проверять exists()

        Args:
            user: Пользователь
            book_id: ID книги

        Returns:
            Tuple[bool, str]: (в избранном ли сейчас, действие)
            Например: (True, 'added') или (False, 'removed')
        """
        if is_book_in_favorites(user, book_id):
            FavoriteRepository.remove_from_favorites(user, book_id)
            return False, 'removed'
        else:
            FavoriteRepository.add_to_favorites(user, book_id)
            return True, 'added'

    @staticmethod
    @transaction.atomic
    def clear_favorites(user: User) -> int:
        deleted_count, _ = Favorite.objects.filter(user=user).delete()
        return deleted_count