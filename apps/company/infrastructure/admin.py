from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.company.infrastructure.models import (AboutCompany, Company,
                                                ContactDetail, SocialMedia)


@admin.register(Company)
class CompanyAdmin(TranslatableAdmin):
    list_display = ("name", "logo_preview")
    readonly_fields = ("logo_preview",)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" />', obj.logo.url)
        return "Logo doesn't exist"


@admin.register(AboutCompany)
class AboutCompanyAdmin(TranslatableAdmin):
    list_display = ("title", "image_preview")
    readonly_fields = ("image_preview",)

    fieldsets = (
        (_("Main"), {"fields": ("title", "content")}),
        (_("Image"), {"fields": ("image", "image_preview")}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Image doesn't exist"


@admin.register(ContactDetail)
class ContactDetailAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "icon_preview")

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="100" />', obj.icon.url)
        return "Icon doesn't exist"
