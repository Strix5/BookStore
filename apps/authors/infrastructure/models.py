from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from commons.models.abstract_models import AbstractDateTimeModel


class Author(TranslatableModel, AbstractDateTimeModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255)
    )
    image = models.ImageField(
        upload_to="authors/",
        max_length=255,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)
