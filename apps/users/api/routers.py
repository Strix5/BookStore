from rest_framework.routers import DefaultRouter

from apps.users.api.views import UserProfileViewSet, UserViewSet


router = DefaultRouter()

router.register("users", UserViewSet, basename="user")
router.register("profiles", UserProfileViewSet, basename="profile")
