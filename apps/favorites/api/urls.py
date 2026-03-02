from django.urls import path, include

from apps.favorites.api.routers import router


app_name = 'favorites'

urlpatterns = [
    path('', include(router.urls)),
]