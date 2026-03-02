from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from apps.books.infrastructure.models import Book


class Recommendation(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        description=models.TextField(blank=True, null=True),
        image=models.ImageField(
            upload_to="recommendations/",
            max_length=255,
            blank=True,
            null=True
        )
    )
    slug = models.SlugField(unique=True, max_length=255)
    books = models.ManyToManyField(
        to=Book,
        through="RecommendationBook",
        related_name="recommended_books"
    )
    created_at = models.DateField(
        default=now,
        verbose_name=_("Publish Date")
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Recommendation")
        verbose_name_plural = _("Recommendations")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class RecommendationBook(models.Model):
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name="recommendation_books"
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="book_recommendations"
    )

    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order",)
        unique_together = ("recommendation", "book")

    def __str__(self):
        return f"{self.recommendation} → {self.book}"
