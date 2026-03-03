from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.services.infrastructure.models import Service, ServiceGroup


@admin.register(ServiceGroup)
class ServiceGroupAdmin(TranslatableAdmin):
    list_display = ("name", "is_active", "order", "image_preview")
    list_editable = ("is_active", "order")
    readonly_fields = ("slug", "image_preview", "created_at", "updated_at")
    search_fields = ("translations__name",)
    list_per_page = 20

    fieldsets = (
        (_("Main"), {"fields": ("name", "description", "order", "is_active")}),
        (_("Image"), {"fields": ("image", "image_preview")}),
        (_("Metadata"), {"fields": ("slug", "created_at", "updated_at")}),
    )

    def image_preview(self, obj):
        image = obj.safe_translation_getter("image", any_language=True)
        if image:
            return format_html('<img src="{}" width="100" />', image.url)
        return _("Image doesn't exist")


@admin.register(Service)
class ServiceAdmin(TranslatableAdmin):
    list_display = ("name", "order", "is_active", "group", "image_preview")
    list_editable = ("order", "is_active")
    readonly_fields = ("slug", "image_preview", "created_at", "updated_at")
    search_fields = ("translations__name",)
    list_per_page = 20

    fieldsets = (
        (_("Main"), {"fields": ("name", "description", "group", "order", "is_active")}),
        (_("Image"), {"fields": ("image", "image_preview")}),
        (_("Metadata"), {"fields": ("slug", "created_at", "updated_at")}),
    )

    def image_preview(self, obj):
        image = obj.safe_translation_getter("image", any_language=True)
        if image:
            return format_html('<img src="{}" width="100" />', image.url)
        return _("Image doesn't exist")
