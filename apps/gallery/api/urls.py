from django.urls import path, include

from apps.gallery.api.routers import router


urlpatterns = (
    path("", include(router.urls)),
)
