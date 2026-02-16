from rest_framework.routers import DefaultRouter

from apps.cart.api.views import CartViewSet, FavoriteViewSet


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

favorites - базовый URL: /api/favorites/
Автоматически создаются endpoints:
- GET    /api/favorites/                  - list
- POST   /api/favorites/add/              - add action
- DELETE /api/favorites/remove/{book_id}/ - remove action
- POST   /api/favorites/toggle/           - toggle action
- DELETE /api/favorites/clear/            - clear action
- GET    /api/favorites/check/{book_id}/  - check action
"""
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
