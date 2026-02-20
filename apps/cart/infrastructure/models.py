from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from commons.models.abstract_models import AbstractDateTimeModel
from apps.books.infrastructure.models import Book


class Cart(AbstractDateTimeModel):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        return f"Cart of {self.user.nickname}"

    @property
    def total_items(self) -> int:
        return self.items.aggregate(
            total=Sum('quantity')
        )['total'] or 0


class CartItem(AbstractDateTimeModel):
    cart = models.ForeignKey(
        to=Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    book = models.ForeignKey(
        to=Book,
        on_delete=models.CASCADE,
        related_name="in_carts",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("Minimum quantity is 1")
    )

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        unique_together = [["cart", "book"]]
        indexes = [
            models.Index(fields=["cart", "book"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.book.name} : {self.quantity}"

    @property
    def subtotal(self) -> float:
        return self.book.price * self.quantity


class Favorite(AbstractDateTimeModel):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    book = models.ForeignKey(
        to=Book,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )

    class Meta:
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")
        unique_together = [["user", "book"]]
        indexes = [
            models.Index(fields=["user", "book"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.nickname} ♥ {self.book.name}"
