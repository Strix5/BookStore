from django.db.models.signals import post_delete
from django.dispatch import receiver

from commons.services.media_deletion import delete_instance_files


def connect_media_cleanup(model_cls):
    @receiver([post_delete], sender=model_cls)
    def delete_media(sender, instance, **kwargs):
        delete_instance_files(instance)
