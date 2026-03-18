from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.books.api.serializers import (BookCategorySerializer,
                                        BookDetailSerializer,
                                        BookListSerializer)
from apps.books.infrastructure.selectors import (get_active_categories,
                                                 search_books, get_allowed_books_by_category)
from apps.books.interface.paginations import CustomBooksPagination


class BookViewSet(ReadOnlyModelViewSet):
    pagination_class = CustomBooksPagination
    lookup_field = "slug"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_age = getattr(self.request.user, "age", 0)
        query = self.request.query_params.get("search")
        return search_books(query=query, user_age=user_age)

    def get_serializer_class(self):
        return BookListSerializer if self.action == "list" else BookDetailSerializer


class BookCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = BookCategorySerializer
    lookup_field = "slug"
    pagination_class = CustomBooksPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_active_categories()

    def get_object(self):
        slug = self.kwargs[self.lookup_field]
        obj = self.get_queryset().filter(slug=slug).first()

        if obj is None:
            raise NotFound()

        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["get"], url_path="books")
    def books(self, request, slug: str = None):
        user_age = getattr(request.user, "age", 0)

        category_exists = self.get_queryset().filter(slug=slug).exists()
        if not category_exists:
            raise NotFound()

        qs = get_allowed_books_by_category(slug=slug, user_age=user_age)

        page = self.paginate_queryset(qs)
        serializer = BookListSerializer(page, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)
