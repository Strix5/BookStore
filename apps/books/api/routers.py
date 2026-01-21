from rest_framework.routers import DefaultRouter

from apps.books.api.views import BookViewSet, BookCategoryViewSet

router = DefaultRouter()

router.register(r"books", BookViewSet, basename="book")
router.register(r"book-categories", BookCategoryViewSet, basename="book-category")
