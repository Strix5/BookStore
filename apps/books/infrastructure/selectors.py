from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count, F, Max, Q, QuerySet
from django.db.models.query import Prefetch

from apps.authors.infrastructure.models import Author
from apps.books.infrastructure.models import Book, BookCategory


def get_allowed_books(user_age: int) -> QuerySet:
    qs = Book.objects.filter(is_active=True).prefetch_related(Prefetch("translations"),
            Prefetch(
                "author",
                queryset=Author.objects.prefetch_related("translations"),
            ),
            Prefetch(
                "category",
                queryset=BookCategory.objects.prefetch_related("translations"),
            )
        ).order_by("-created_at")

    if user_age < 18:
        qs = qs.filter(is_adult=False)

    return qs


def get_allowed_books_by_category(slug: str, user_age: int) -> QuerySet:
    qs = (
        Book.objects.filter(is_active=True, category__slug=slug)
        .prefetch_related(Prefetch("translations"),
            Prefetch(
                "author",
                queryset=Author.objects.prefetch_related("translations"),
            ),
            Prefetch(
                "category",
                queryset=BookCategory.objects.prefetch_related("translations"),
            )
        )
        .distinct()
    )

    if user_age < 18:
        qs = qs.filter(is_adult=False)

    return qs


def search_books(*, query: str | None, user_age: int) -> QuerySet:
    qs = get_allowed_books(user_age=user_age)

    if not query:
        return qs

    return (
        qs.annotate(
            name_similarity=Max(
                TrigramSimilarity("translations__name", query)
            ),
            author_similarity_raw=Max(
                TrigramSimilarity("author__translations__name", query)
            ),
        )
        .annotate(
            total_similarity=F("name_similarity") + F("author_similarity_raw") * 0.7
        )
        .filter(total_similarity__gt=0.2)
        .order_by("-total_similarity")
        .distinct()
    )


def get_active_categories() -> QuerySet:
    return (
        BookCategory.objects.filter(is_active=True)
        .prefetch_related("translations")
        .annotate(
            books_count=Count(
                "books",
                filter=Q(books__is_active=True),
                distinct=True,
            )
        )
        .order_by("-created_at")
    )
