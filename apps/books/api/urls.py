from django.urls import include, path

from apps.books.api.routers import router

urlpatterns = (path("", include(router.urls)),)
