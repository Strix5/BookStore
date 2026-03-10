from django.db.models import Prefetch

from apps.galleries.infrastructure.models import Gallery, GalleryItem


def get_active_galleries():
    return (
        Gallery.objects
        .filter(is_active=True)
        .prefetch_related("translations")
        .order_by("order")
    )


def get_active_gallery_by_slug(*, slug: str):
    active_items_qs = (
        GalleryItem.objects
        .filter(is_active=True)
        .only(
            "id", "gallery_id", "item_type",
            "image", "original_video",
            "hls_master_playlist", "hls_status",
            "order",
        )
        .order_by("order")
    )

    return (
        Gallery.objects
        .filter(is_active=True, slug=slug)
        .prefetch_related(
            "translations",
            Prefetch("items", queryset=active_items_qs),
        )
        .first()
    )


def get_active_gallery_items_by_gallery_slug(*, slug: str):
    return (
        GalleryItem.objects
        .filter(is_active=True, gallery__slug=slug)
        .order_by("order")
    )
