from rest_framework.routers import DefaultRouter

from apps.orders.api.views import OrderViewSet


#   GET  /orders/           → list
#   GET  /orders/{id}/      → retrieve
#   POST /orders/purchase/  → purchase (@action)
router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
