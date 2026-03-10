from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_spectacular.utils import extend_schema

from apps.galleries.interface.paginations import CustomGalleryPagination
from apps.galleries.api.serializers import (
    GalleryListSerializer,
    GalleryDetailSerializer,
    GalleryItemSerializer,
)
from apps.galleries.interface.api_schema import (
    gallery_list_schema,
    gallery_retrieve_schema,
    gallery_items_schema,
)
from apps.galleries.infrastructure.selectors import (
    get_active_galleries,
    get_active_gallery_by_slug,
    get_active_gallery_items_by_gallery_slug,
)


@extend_schema(tags=["Gallery"])
class GalleryViewSet(ReadOnlyModelViewSet):
    pagination_class = CustomGalleryPagination
    lookup_field = "slug"
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_active_galleries()

    def get_serializer_class(self):
        if self.action == "list":
            return GalleryListSerializer
        return GalleryDetailSerializer

    @extend_schema(**gallery_list_schema)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**gallery_retrieve_schema)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_object(self):
        slug = self.kwargs[self.lookup_field]
        obj = get_active_gallery_by_slug(slug=slug)

        if obj is None:
            raise NotFound()

        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(**gallery_items_schema)
    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, slug: str = None):
        gallery_exists = get_active_gallery_by_slug(slug=slug)
        if gallery_exists is None:
            raise NotFound()

        qs = get_active_gallery_items_by_gallery_slug(slug=slug)
        page = self.paginate_queryset(qs)
        serializer = GalleryItemSerializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)
