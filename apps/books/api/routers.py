from rest_framework.routers import DefaultRouter

from apps.books.api.views import BookCategoryViewSet, BookViewSet

router = DefaultRouter()

router.register(r"books", BookViewSet, basename="book")
router.register(r"book-categories", BookCategoryViewSet, basename="book-category")
