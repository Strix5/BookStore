from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.books.infrastructure.models import Book, BookCategory


@admin.register(Book)
class BookAdmin(TranslatableAdmin):
    list_display = (
        "name", "author", "category",
        "is_active", "image_preview"
    )
    list_editable = ("is_active",)
    list_filter = ("created_at",)
    list_per_page = 20
    readonly_fields = ("image_preview", "slug", "updated_at", "created_at")
    search_fields = ("translations__name", "slug")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (_("Main"), {"fields": ("name", "description", "category", "author", "is_active", "is_adult")}),
        (_("Image"), {"fields": ("file", "image", "image_preview")}),
        (_("Metadata"), {"fields": ("slug", "created_at", "updated_at")}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Image doesn't exist"


@admin.register(BookCategory)
class BookCategoryAdmin(TranslatableAdmin):
    list_display = ("name", "is_active", "image_preview")
    list_editable = ("is_active",)
    list_filter = ("created_at",)
    list_per_page = 20
    readonly_fields = ("image_preview", "slug", "updated_at", "created_at")
    search_fields = ("translations__name", "slug")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (_("Main"), {"fields": ("name", "is_active")}),
        (_("Image"), {"fields": ("image", "image_preview")}),
        (_("Metadata"), {"fields": ("slug", "created_at", "updated_at")}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Image doesn't exist"
