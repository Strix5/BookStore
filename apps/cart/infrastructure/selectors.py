from typing import Optional

from django.db import models
from django.db.models import QuerySet, Sum, Prefetch
from django.contrib.auth import get_user_model

from apps.cart.infrastructure.models import Cart, CartItem, Favorite

User = get_user_model()


def get_or_create_cart(user: User) -> Cart:
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def get_cart_with_items(user: User) -> Optional[Cart]:
    try:
        return Cart.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=CartItem.objects.select_related(
                    'book'
                ).prefetch_related(
                    'book__translations',
                    'book__category',
                    'book__author'
                ).order_by('-created_at')
            )
        ).filter(is_active=True, user=user).first()
    except Cart.DoesNotExist:
        return None


def get_cart_items(user: User) -> QuerySet[CartItem]:
    cart = get_or_create_cart(user)

    return CartItem.objects.filter(
        cart=cart
    ).select_related(
        'book'
    ).prefetch_related(
        'book__translations',
        'book__category__translations',
        'book__author'
    ).order_by('-created_at')


def get_cart_item(user: User, book_id: int) -> Optional[CartItem]:
    """
    Получает конкретный элемент корзины.

    Зачем:
    - Проверка наличия книги в корзине
    - Получение текущего количества
    - Обновление количества

    Args:
        user: Пользователь
        book_id: ID книги

    Returns:
        CartItem или None
    """
    cart = get_or_create_cart(user)

    try:
        return CartItem.objects.select_related('book').get(
            cart=cart,
            book_id=book_id
        )
    except CartItem.DoesNotExist:
        return None


def get_cart_summary(user: User) -> dict:
    cart = get_or_create_cart(user)

    summary = cart.items.aggregate(
        total_items=Sum('quantity'),
        unique_books=models.Count('id')
    )

    return {
        'total_items': summary['total_items'] or 0,
        'unique_books': summary['unique_books'] or 0,
        'total_price': summary['total_price'] or 0
    }


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
