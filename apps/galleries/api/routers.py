from rest_framework.routers import DefaultRouter

from apps.galleries.api.views import GalleryViewSet


router = DefaultRouter()

router.register(r"galleries", GalleryViewSet, basename="gallery")
