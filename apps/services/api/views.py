from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema

from apps.services.interface.paginations import CustomServicePagination
from apps.services.api.serializers import (
    ServiceGroupListSerializer,
    ServiceGroupDetailSerializer,
    ServiceListSerializer,
    ServiceDetailSerializer,
)
from apps.services.interface.api_schema import (
    service_group_list_schema,
    service_group_retrieve_schema,
    service_group_services_schema,
    service_list_schema,
    service_retrieve_schema,
)
from apps.services.infrastructure.selectors import (
    get_active_service_groups,
    get_active_service_group_by_slug,
    get_active_services,
    get_active_services_by_group_slug,
)


@extend_schema(tags=["Service Groups"])
class ServiceGroupViewSet(ReadOnlyModelViewSet):
    pagination_class = CustomServicePagination
    lookup_field = "slug"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_active_service_groups()

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceGroupListSerializer
        return ServiceGroupDetailSerializer

    @extend_schema(**service_group_list_schema)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**service_group_retrieve_schema)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_object(self):
        slug = self.kwargs[self.lookup_field]
        obj = get_active_service_group_by_slug(slug=slug)

        if obj is None:
            raise NotFound()

        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(**service_group_services_schema)
    @action(detail=True, methods=["get"], url_path="services")
    def services(self, request, slug: str = None):
        group_exists = get_active_service_group_by_slug(slug=slug)
        if group_exists is None:
            raise NotFound()

        qs = get_active_services_by_group_slug(slug=slug)
        page = self.paginate_queryset(qs)
        serializer = ServiceListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema(tags=["Services"])
class ServiceViewSet(ReadOnlyModelViewSet):
    pagination_class = CustomServicePagination
    lookup_field = "slug"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_active_services()

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceListSerializer
        return ServiceDetailSerializer

    @extend_schema(**service_list_schema)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**service_retrieve_schema)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
