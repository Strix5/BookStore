from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.books.infrastructure.models import Book, BookCategory
from commons.services.slug_generation import generate_slug
from commons.signals.media import connect_media_cleanup


@receiver(pre_save, sender=BookCategory)
@receiver(pre_save, sender=Book)
def book_slug_signal(sender, instance, **kwargs):
    generate_slug(instance, sender, "name")


for obj in [Book, BookCategory]:
    connect_media_cleanup(obj)
