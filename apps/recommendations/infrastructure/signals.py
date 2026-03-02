from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.recommendations.infrastructure.models import Recommendation
from commons.services.slug_generation import generate_slug
from commons.signals.media import connect_media_cleanup


@receiver(pre_save, sender=Recommendation)
def recommendation_slug_signal(sender, instance, **kwargs):
    generate_slug(instance, sender, "title")


for obj in [Recommendation]:
    connect_media_cleanup(obj)
