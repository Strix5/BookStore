from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.services.infrastructure.models import ServiceGroup, Service
from commons.services.slug_generation import generate_slug
from commons.signals.media import connect_media_cleanup


@receiver(pre_save, sender=ServiceGroup)
def service_group_slug_signal(sender, instance, **kwargs):
    generate_slug(instance, sender, "name")


@receiver(pre_save, sender=Service)
def service_slug_signal(sender, instance, **kwargs):
    generate_slug(instance, sender, "name")


for model in [ServiceGroup, Service]:
    connect_media_cleanup(model)
