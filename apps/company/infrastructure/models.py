from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from parler.models import TranslatableModel, TranslatedFields


class Company(TranslatableModel):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False
    )
    translations = TranslatedFields(
        name=models.CharField(max_length=255)
    )
    logo = models.ImageField(
        upload_to="company/logo/",
        max_length=255,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Company Name & Logo")
        verbose_name_plural = _("Company Name & Logo")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)


class AboutCompany(TranslatableModel):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False
    )
    translations = TranslatedFields(
        title=models.CharField(max_length=255),
        content=RichTextField()
    )
    image = models.ImageField(
        upload_to="company/image/",
        max_length=255,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Company Information")
        verbose_name_plural = _("Company Information")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class SocialMedia(models.Model):
    icon = models.FileField(
        upload_to="company/socials/",
        max_length=255,
    )
    link = models.URLField(max_length=255)

    class Meta:
        verbose_name = _("Company Social Media")
        verbose_name_plural = _("Company Social Media")


class ContactDetail(models.Model):
    id = models.PositiveSmallIntegerField(
        primary_key=True,
        default=1,
        editable=False
    )
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)
    social_media = models.ManyToManyField(
        to=SocialMedia,
        blank=True
    )

    class Meta:
        verbose_name = _("Company Contact Detail")
        verbose_name_plural = _("Company Contact Details")
