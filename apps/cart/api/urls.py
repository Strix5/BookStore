from django.urls import path, include

from apps.cart.api.routers import router


app_name = 'cart'

urlpatterns = [
    path('', include(router.urls)),
]