from django.urls import path, include

from apps.books.api.routers import router


urlpatterns = (
    path("", include(router.urls)),
)
