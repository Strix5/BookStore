from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.books.infrastructure import Book
from commons.models.abstract_models import AbstractDateTimeModel


class Order(AbstractDateTimeModel):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices,
        default=StatusChoices.PENDING,
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Order #{self.pk} -- {self.user} -- {self.status}"


class OrderItem(AbstractDateTimeModel):
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    book = models.ForeignKey(
        to=Book,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        unique_together = ("book", "order")

    def __str__(self) -> str:
        return f"{self.book}: {self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity
