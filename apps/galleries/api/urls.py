from django.urls import path, include

from apps.galleries.api.routers import router


urlpatterns = (
    path("", include(router.urls)),
)
