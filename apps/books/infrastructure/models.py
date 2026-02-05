from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from apps.authors.infrastructure.models import Author
from apps.books.common.book_model import AbstractDateTimeModel


class BookCategory(TranslatableModel, AbstractDateTimeModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255)
    )
    image = models.ImageField(
        upload_to="book_categories/",
        max_length=255,
        blank=True,
        null=True,
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Book Category")
        verbose_name_plural = _("Book Categories")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)


class Book(TranslatableModel, AbstractDateTimeModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, db_index=True),
        description=RichTextField(blank=True, null=True),
    )
    category = models.ManyToManyField(
        to=BookCategory,
        related_name="books"
    )
    author = models.ManyToManyField(
        to=Author,
        related_name="author_books",
    )
    file = models.FileField(
        upload_to="books/files/",
        max_length=255,
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to="books/images/",
        max_length=255,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_adult = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)
