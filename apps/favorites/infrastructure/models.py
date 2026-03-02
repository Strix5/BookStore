from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from commons.models.abstract_models import AbstractDateTimeModel
from apps.books.infrastructure.models import Book


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