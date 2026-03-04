from apps.services.infrastructure.models import ServiceGroup, Service
from django.db.models import Prefetch


def get_active_service_groups():
    active_services_qs = (
        Service.objects
        .filter(is_active=True)
        .prefetch_related("translations")
        .order_by("order")
    )

    return (
        ServiceGroup.objects
        .filter(is_active=True)
        .prefetch_related(
            "translations",
            Prefetch("services", queryset=active_services_qs),
        )
        .order_by("order")
    )


def get_active_service_group_by_slug(*, slug: str):
    active_services_qs = (
        Service.objects
        .filter(is_active=True)
        .prefetch_related("translations")
        .order_by("order")
    )

    return (
        ServiceGroup.objects
        .filter(is_active=True, slug=slug)
        .prefetch_related(
            "translations",
            Prefetch("services", queryset=active_services_qs),
        )
        .first()
    )


def get_active_services():
    return (
        Service.objects
        .filter(is_active=True)
        .select_related("group")
        .prefetch_related("translations", "group__translations")
        .order_by("group__order", "order")
    )


def get_active_services_by_group_slug(*, slug: str):
    return (
        Service.objects
        .filter(is_active=True, group__slug=slug)
        .prefetch_related("translations")
        .order_by("order")
    )
