from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from apps.users.infrastructure.models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    max_num = 1
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    ordering = ("email",)
    list_display = (
        "email",
        "nickname",
        "is_staff",
        "is_superuser",
        "is_active",
        "profile_avatar_thumb",
    )
    list_editable = ("is_active",)
    search_fields = ("email", "nickname")

    fieldsets = (
        (None, {"fields": ("email", "nickname", "password", "age")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "nickname",
                    "first_name",
                    "last_name",
                    "age",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )

    def profile_bio(self, obj):
        if hasattr(obj, "profile") and obj.profile:
            return (
                (obj.profile.biography[:50] + "…")
                if len(obj.profile.biography) > 50
                else obj.profile.biography
            )
        return "-"

    profile_bio.short_description = "Biography"

    def profile_avatar_thumb(self, obj):
        if hasattr(obj, "profile") and obj.profile and obj.profile.avatar:
            return format_html(
                '<img src="{}" style="height:50px;width:auto;border-radius:4px;" />',
                obj.profile.avatar.url,
            )
        return "-"

    profile_avatar_thumb.short_description = "Avatar"
