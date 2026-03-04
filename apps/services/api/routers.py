from rest_framework.routers import DefaultRouter

from apps.services.api.views import ServiceGroupViewSet, ServiceViewSet


# Регистрируем два ViewSet-а в одном роутере приложения services.
#
# Итоговые маршруты:
#   GET  /service-groups/                     -> ServiceGroupViewSet.list
#   GET  /service-groups/{slug}/              -> ServiceGroupViewSet.retrieve
#   GET  /service-groups/{slug}/services/     -> ServiceGroupViewSet.services (action)
#
#   GET  /services/                           -> ServiceViewSet.list
#   GET  /services/{slug}/                    -> ServiceViewSet.retrieve

router = DefaultRouter()

router.register(r"service-groups", ServiceGroupViewSet, basename="service-group")
router.register(r"services", ServiceViewSet, basename="service")