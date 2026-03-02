from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.favorites.infrastructure.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_link',
        'book_link',
        'created_at'
    ]

    list_filter = [
        'created_at'
    ]

    search_fields = [
        'user__email',
        'user__nickname',
        'book__translations__name'
    ]

    readonly_fields = [
        'user',
        'book',
        'created_at'
    ]

    ordering = ['-created_at']
    list_per_page = 25

    date_hierarchy = 'created_at'

    def user_link(self, obj):
        return format_html(
            '<a href="/admin-panel/users/customuser/{}/change/">{}</a>',
            obj.user.id,
            obj.user.nickname
        )

    user_link.short_description = _("User")
    user_link.admin_order_field = 'user__nickname'

    def book_link(self, obj):
        return format_html(
            '<a href="/admin-panel/books/book/{}/change/">{}</a>',
            obj.book.id,
            obj.book.name
        )

    book_link.short_description = _("Book")
    book_link.admin_order_field = 'book__translations__name'

    def has_add_permission(self, request):
        return False
