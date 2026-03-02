from rest_framework.routers import DefaultRouter

from apps.favorites.api.views import FavoriteViewSet


router = DefaultRouter()

"""
Регистрация ViewSet'ов.

favorites - базовый URL: /api/favorites/
Автоматически создаются endpoints:
- GET    /api/favorites/                  - list
- POST   /api/favorites/add/              - add action
- DELETE /api/favorites/remove/{book_id}/ - remove action
- POST   /api/favorites/toggle/           - toggle action
- DELETE /api/favorites/clear/            - clear action
- GET    /api/favorites/check/{book_id}/  - check action
"""
router.register(r'favorites', FavoriteViewSet, basename='favorite')
