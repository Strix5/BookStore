from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from apps.books.infrastructure.models import Book, BookCategory
from commons.services.media_deletion import delete_instance_files
from commons.services.slug_generation import generate_slug


@receiver(pre_save, sender=BookCategory)
@receiver(pre_save, sender=Book)
def article_slug_signal(sender, instance, **kwargs):
    generate_slug(instance, sender, "name")


def connect_media_cleanup(model_cls):
    @receiver([post_delete], sender=model_cls)
    def delete_media(sender, instance, **kwargs):
        delete_instance_files(instance)


for obj in [
    Book,
    BookCategory
]:
    connect_media_cleanup(obj)
