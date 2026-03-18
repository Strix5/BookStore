import django_filters

from apps.books.infrastructure.models import Book, BookCategory


class BookFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Price from",
    )
    price_max = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Price to",
    )
    created_at_after = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
        label="Added after",
    )
    created_at_before = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
        label="Added before",
    )
    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category__slug",
        to_field_name="slug",
        queryset=BookCategory.objects.filter(is_active=True),
        label="Category (slug)",
    )

    author = django_filters.BaseInFilter(
        field_name="author__slug",
        lookup_expr="in",
        label="Author (slug: ?author=magtymguly,rowling)",
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("price", "price"),
            ("created_at", "created_at"),
        ),
        label="Sorting",
    )

    class Meta:
        model = Book
        # Fields unnecessary. Empty list means not to add auto filters.
        fields = []


class BookCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="translations__name",
        lookup_expr="icontains",
        label="Name",
    )

    class Meta:
        model = BookCategory
        fields = []
