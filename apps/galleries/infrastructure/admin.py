from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.galleries.infrastructure.models import Gallery, GalleryItem


class GalleryItemInline(admin.TabularInline):
    model = GalleryItem
    extra = 1
    ordering = ("order",)
    show_change_link = True
    fields = ("preview", "item_type", "image", "original_video", "order", "is_active", "hls_status")
    readonly_fields = ("preview", "hls_status")

    def preview(self, obj: GalleryItem) -> str:
        if obj.item_type == GalleryItem.ItemType.IMAGE and obj.image:
            return format_html('<img src="{}" width="80" />', obj.image.url)
        if obj.item_type == GalleryItem.ItemType.VIDEO:
            status = obj.get_hls_status_display()
            return format_html('<span style="color: gray;">▶ {}</span>', status)
        return "—"

    preview.short_description = _("Preview")


@admin.register(Gallery)
class GalleryAdmin(TranslatableAdmin):
    list_display = ("name", "order", "is_active", "cover_preview")
    list_editable = ("order", "is_active")
    list_per_page = 20
    readonly_fields = ("slug", "cover_preview", "created_at", "updated_at")
    inlines = (GalleryItemInline,)

    fieldsets = (
        (_("Main"), {"fields": ("name", "description", "order", "is_active")}),
        (_("Cover"), {"fields": ("cover", "cover_preview")}),
        (_("Meta"), {"fields": ("slug", "created_at", "updated_at")}),
    )

    def cover_preview(self, obj: Gallery):
        if obj.cover:
            return format_html('<img src="{}" width="120" />', obj.cover.url)
        return _("No cover")

    cover_preview.short_description = _("Main galleries cover preview")


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = (
        "id", "gallery", "item_type", "order",
        "is_active", "hls_status_badge",
    )
    list_filter = ("gallery", "item_type", "hls_status", "is_active")
    list_editable = ("order", "is_active")
    list_per_page = 20
    readonly_fields = ("created_at", "updated_at", "hls_status", "hls_error", "hls_master_playlist", "media_preview")
    actions = ("retry_hls_conversion",)

    fieldsets = (
        (_("Media"), {"fields": ("gallery", "item_type", "image", "original_video", "order", "is_active")}),
        (_("HLS"), {"fields": ("hls_status", "hls_error", "hls_master_playlist")}),
        (_("Preview"), {"fields": ("media_preview", "created_at", "updated_at")}),
    )

    def hls_status_badge(self, obj: GalleryItem) -> str:
        colors = {
            "pending":    "gray",
            "processing": "orange",
            "ready":      "green",
            "failed":     "red",
        }
        color = colors.get(obj.hls_status, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_hls_status_display(),
        )

    hls_status_badge.short_description = _("HLS Status")

    def media_preview(self, obj: GalleryItem) -> str:
        if obj.item_type == GalleryItem.ItemType.IMAGE and obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        if obj.item_type == GalleryItem.ItemType.VIDEO and obj.is_video_ready:
            return format_html(
                '<a href="{}" target="_blank">Open master.m3u8</a>',
                obj.hls_master_playlist.url,
            )
        return "—"

    media_preview.short_description = _("Preview")

    @admin.action(description=_("Retry HLS conversion for selected videos"))
    def retry_hls_conversion(self, request, queryset):
        from apps.galleries.infrastructure.tasks import process_video_to_hls

        video_items = queryset.filter(
            item_type=GalleryItem.ItemType.VIDEO,
            original_video__isnull=False,
        ).exclude(original_video="")

        count = 0
        for item in video_items:
            process_video_to_hls.delay(item.pk)
            count += 1

        self.message_user(request, _(f"Queued HLS conversion for {count} video(s)."))
