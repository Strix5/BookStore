from django.db.models import QuerySet
from django.contrib.auth import get_user_model

from apps.favorites.infrastructure.models import Favorite

User = get_user_model()


def get_user_favorites(user: User) -> QuerySet[Favorite]:
    """
    Получает все избранные книги пользователя.

    Зачем prefetch:
    - Загружаем книги вместе с переводами и категориями
    - Один запрос вместо N+1

    Args:
        user: Пользователь

    Returns:
        QuerySet избранных книг
    """
    return Favorite.objects.filter(
        user=user
    ).select_related(
        'book'
    ).prefetch_related(
        'book__translations',
        'book__category__translations',
        'book__author'
    ).order_by('-created_at')


def get_favorite_books(user: User) -> QuerySet:
    """
    Получает QuerySet только книг из избранного.

    Зачем:
    - Удобно для отображения: не нужна промежуточная модель Favorite
    - Можно применить фильтры Book (по категории, автору и т.д.)
    - values_list для получения только ID (для проверок)

    Args:
        user: Пользователь

    Returns:
        QuerySet книг
    """
    from apps.books.infrastructure.models import Book

    favorite_book_ids = Favorite.objects.filter(
        user=user
    ).values_list('book_id', flat=True)

    return Book.objects.filter(
        id__in=favorite_book_ids,
        is_active=True
    ).prefetch_related(
        'translations',
        'category__translations',
        'author'
    )


def is_book_in_favorites(user: User, book_id: int) -> bool:
    return Favorite.objects.filter(
        user=user,
        book_id=book_id
    ).exists()


def get_favorites_count(user: User) -> int:
    return Favorite.objects.filter(user=user).count()
