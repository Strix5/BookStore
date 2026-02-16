from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.cart.infrastructure.models import Cart, CartItem, Favorite


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    can_delete = False

    readonly_fields = [
        'book',
        'quantity',
        'book_info',
        'created_at',
        'updated_at'
    ]

    fields = [
        'book_info',
        'quantity',
        'created_at',
        'updated_at'
    ]

    def book_info(self, obj):
        if obj.book:
            active_badge = "✓" if obj.book.is_active else "✗"
            return format_html(
                '<a href="/admin/books/book/{}/change/">{}</a> {}',
                obj.book.id,
                obj.book.name,
                active_badge
            )
        return "-"

    book_info.short_description = _("Book")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_link',
        'items_count',
        'total_quantity',
        'created_at',
        'updated_at'
    ]

    list_filter = [
        'created_at',
        'updated_at'
    ]

    search_fields = [
        'user__email',
        'user__nickname'
    ]

    readonly_fields = [
        'user',
        'items_count',
        'total_quantity',
        'created_at',
        'updated_at'
    ]
    inlines = [CartItemInline]
    ordering = ['-created_at']
    list_per_page = 25

    def user_link(self, obj):
        return format_html(
            '<a href="/admin/users/customuser/{}/change/">{} ({})</a>',
            obj.user.id,
            obj.user.email,
            obj.user.nickname
        )

    user_link.short_description = _("User")
    user_link.admin_order_field = 'user__email'

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = _("Unique Books")

    def total_quantity(self, obj):
        return obj.total_items

    total_quantity.short_description = _("Total Items")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'cart_user',
        'book_link',
        'quantity',
        'created_at',
        'updated_at'
    ]

    list_filter = [
        'created_at',
        'updated_at',
        'quantity'
    ]

    search_fields = [
        'cart__user__email',
        'cart__user__nickname',
        'book__translations__name'
    ]

    readonly_fields = [
        'cart',
        'book',
        'quantity',
        'created_at',
        'updated_at'
    ]

    ordering = ['-created_at']
    list_per_page = 25

    def cart_user(self, obj):
        return format_html(
            '<a href="/admin/cart/cart/{}/change/">{}</a>',
            obj.cart.id,
            obj.cart.user.nickname
        )

    cart_user.short_description = _("User")
    cart_user.admin_order_field = 'cart__user__nickname'

    def book_link(self, obj):
        return format_html(
            '<a href="/admin/books/book/{}/change/">{}</a>',
            obj.book.id,
            obj.book.name
        )

    book_link.short_description = _("Book")
    book_link.admin_order_field = 'book__translations__name'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
            '<a href="/admin/users/customuser/{}/change/">{}</a>',
            obj.user.id,
            obj.user.nickname
        )

    user_link.short_description = _("User")
    user_link.admin_order_field = 'user__nickname'

    def book_link(self, obj):
        return format_html(
            '<a href="/admin/books/book/{}/change/">{}</a>',
            obj.book.id,
            obj.book.name
        )

    book_link.short_description = _("Book")
    book_link.admin_order_field = 'book__translations__name'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False