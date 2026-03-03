from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from commons.models.abstract_models import AbstractDateTimeModel


class ServiceGroup(TranslatableModel, AbstractDateTimeModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True, null=True),
        image=models.ImageField(
            upload_to="service_groups/",
            max_length=255,
            blank=True,
            null=True
        )
    )
    slug = models.SlugField(max_length=255, unique=True)
    order = models.PositiveSmallIntegerField(default=0, help_text=_("Порядок расположения группы."))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Service Group")
        verbose_name_plural = _("Service Groups")
        ordering = ("order",)

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True)


class Service(TranslatableModel, AbstractDateTimeModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=RichTextField(blank=True, null=True),
        image=models.ImageField(
            upload_to="services/",
            max_length=255,
            blank=True,
            null=True
        )
    )
    group = models.ForeignKey(
        to=ServiceGroup,
        on_delete=models.CASCADE,
        related_name="services"
    )

    slug = models.SlugField(unique=True, max_length=255)
    order = models.PositiveSmallIntegerField(default=0, help_text=_("Порядок расположения сервиса."))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ("group__order", "order")

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or f"Service #{self.pk}"

