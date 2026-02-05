from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.authors.infrastructure.models import Author
from commons.services.slug_generation import generate_slug
from commons.signals.media import connect_media_cleanup


@receiver(pre_save, sender=Author)
def author_slug_signal(sender, instance, **kwargs):
    generate_slug(instance, sender, "name")


for obj in [
    Author
]:
    connect_media_cleanup(obj)
