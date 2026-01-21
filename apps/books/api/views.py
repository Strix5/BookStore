from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.books.api.serializers import BookListSerializer, BookDetailSerializer, BookCategorySerializer
from apps.books.interface.use_cases import GetAllowedBooksUseCase
from apps.books.interface.paginations import CustomPagination
from apps.books.infrastructure.repositories import BookRepository
from apps.books.infrastructure.selectors import get_active_categories, get_books_by_category, search_books


class BookViewSet(ReadOnlyModelViewSet):
    pagination_class = CustomPagination
    lookup_field = "slug"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_age = getattr(self.request.user, "age", 0)
        search_item = self.request.query_params.get("search")

        allowed_ids = GetAllowedBooksUseCase(
            book_repository=BookRepository()
        ).execute(user_age=user_age)
        qs = search_books(query=search_item)

        return qs.filter(id__in=allowed_ids)

    def get_serializer_class(self):
        return BookListSerializer if self.action == "list" else BookDetailSerializer


class BookCategoryViewSet(ReadOnlyModelViewSet):
    serializer_class = BookCategorySerializer
    lookup_field = "slug"
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_active_categories()

    @action(detail=True, methods=["get"])
    def books(self, request, slug: str = None):
        user_age = getattr(request.user, "age", 0)

        allowed_ids = GetAllowedBooksUseCase(
            book_repository=BookRepository()
        ).execute(user_age=user_age)
        qs = get_books_by_category(slug=slug).filter(id__in=allowed_ids)

        page = self.paginate_queryset(qs)
        serializer = BookListSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)
