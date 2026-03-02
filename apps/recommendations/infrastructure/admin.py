from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.recommendations.infrastructure.models import Recommendation, RecommendationBook


class RecommendationBookInline(admin.TabularInline):
    model = RecommendationBook
    extra = 1
    autocomplete_fields = ("book",)
    ordering = ("order",)


@admin.register(Recommendation)
class RecommendationAdmin(TranslatableAdmin):
    list_display = ("title", "id", "is_active", "created_at", "image_preview")
    list_editable = ("is_active",)
    list_filter = ("created_at",)
    list_per_page = 20
    readonly_fields = ("slug", "image_preview")

    inlines = (RecommendationBookInline,)

    fieldsets = (
        (_("Main"), {"fields": ("title", "description", "created_at", "is_active")}),
        (_("Image"), {"fields": ("image", "image_preview")}),
        (_("Meta"), {"fields": ("slug",)})
    )

    def image_preview(self, obj):
        image = obj.safe_translation_getter("image", any_language=True)
        if image:
            return format_html('<img src="{}" width="100" />', image.url)
        return _("Image doesn't exist")
