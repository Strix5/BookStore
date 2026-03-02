from django.urls import path, include

from apps.recommendations.api.routers import router


urlpatterns = (
    path("", include(router.urls)),
)
