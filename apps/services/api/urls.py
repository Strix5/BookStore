from django.urls import path, include

from apps.services.api.routers import router

# Финальные URL после подключения в корневом urls.py через path("api/v1/", include(...)):
#
#   GET  /api/v1/service-groups/                  -> список групп
#   GET  /api/v1/service-groups/{slug}/           -> детальная группа + сервисы
#   GET  /api/v1/service-groups/{slug}/services/  -> постраничные сервисы группы
#
#   GET  /api/v1/services/                        -> плоский список всех сервисов
#   GET  /api/v1/services/{slug}/                 -> детальный сервис

urlpatterns = (
    path("", include(router.urls)),
)
