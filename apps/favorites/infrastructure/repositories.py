from typing import Tuple

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

from apps.favorites.infrastructure.models import Favorite
from apps.favorites.infrastructure.selectors import is_book_in_favorites

User = get_user_model()


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
