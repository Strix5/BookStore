from rest_framework.routers import DefaultRouter

from apps.recommendations.api.views import RecommendationViewSet


router = DefaultRouter()

router.register(r"recommendations", RecommendationViewSet, basename="recommendation")
