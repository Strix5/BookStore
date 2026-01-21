from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.authors.infrastructure.models import Author


@admin.register(Author)
class AuthorAdmin(TranslatableAdmin):
    list_display = ("name", "is_active", "image_preview")
    list_editable = ("is_active",)
    list_per_page = 20
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Main"), {"fields": ("name", "is_active")}),
        (_("Image"), {"fields": ("image", "image_preview")}),
        (_("Meta"), {"fields": ("created_at", "updated_at")})
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Image doesn't exist"
