from rest_framework.routers import DefaultRouter

from apps.cart.api.views import CartViewSet


router = DefaultRouter()

"""
Регистрация ViewSet'ов.

cart - базовый URL: /api/cart/
Автоматически создаются endpoints:
- GET    /api/cart/           - list (получить корзину)
- GET    /api/cart/summary/   - summary action
- POST   /api/cart/add/       - add action
- PATCH  /api/cart/update-quantity/{book_id}/ - update_quantity action
- DELETE /api/cart/remove/{book_id}/          - remove action
- DELETE /api/cart/clear/     - clear action
"""
router.register(r'cart', CartViewSet, basename='cart')
