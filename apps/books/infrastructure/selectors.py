from django.contrib.postgres.search import TrigramSimilarity
from django.db import models
from django.db.models import Count, Max

from apps.books.infrastructure.models import Book, BookCategory


def get_active_books():
    return Book.objects.filter(is_active=True).prefetch_related(
        "translations", "category", "author"
    )


def get_active_books_for_entity():
    return Book.objects.filter(is_active=True).only("id", "is_adult")


def get_active_categories():
    return (
        BookCategory.objects.filter(is_active=True)
        .annotate(books_count=Count("books", distinct=True))
        .prefetch_related("translations")
    )


def get_books_by_category(slug: str):
    return (
        Book.objects.filter(is_active=True, category__slug=slug)
        .prefetch_related("translations", "category", "author")
        .distinct()
    )


def search_books(*, query: str | None):
    qs = get_active_books()

    if query:
        qs = qs.annotate(
            name_similarity=Max(TrigramSimilarity('translations__name', query)),
            author_similarity=Max(TrigramSimilarity('author__translations__name', query) * 0.7),
        ).annotate(
            total_similarity=models.F('name_similarity') +
                             models.F('author_similarity')
        ).filter(
            total_similarity__gt=0.2
        ).order_by('-total_similarity')
    return qs.distinct()
