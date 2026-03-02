from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import NotFound

from apps.recommendations.interface.api_schema import recommendation_list_schema, recommendation_retrieve_schema
from apps.recommendations.interface.paginations import CustomRecommendationPagination
from apps.recommendations.api.serializers import (
    RecommendationListSerializer,
    RecommendationDetailSerializer,
)
from apps.recommendations.infrastructure.selectors import (
    get_active_recommendations,
    get_active_recommendation_by_slug,
)


class RecommendationViewSet(ReadOnlyModelViewSet):
    pagination_class = CustomRecommendationPagination
    lookup_field = "slug"
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_active_recommendations()

    def get_serializer_class(self):
        return RecommendationListSerializer if self.action == "list" else RecommendationDetailSerializer

    @extend_schema(**recommendation_list_schema)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**recommendation_retrieve_schema)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_object(self):
        slug = self.kwargs[self.lookup_field]
        obj = get_active_recommendation_by_slug(slug=slug)

        if obj is None:
            raise NotFound()

        self.check_object_permissions(self.request, obj)
        return obj
