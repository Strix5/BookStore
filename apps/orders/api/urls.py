from django.urls import path, include

from apps.orders.api.routers import router

urlpatterns = [
    path("", include(router.urls))
]
