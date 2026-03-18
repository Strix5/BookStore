from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.gallery.infrastructure.models import Gallery, GalleryItem
from commons.services.slug_generation import generate_slug
from commons.signals.media import connect_media_cleanup


@receiver(pre_save, sender=Gallery)
def gallery_slug_signal(sender, instance, **kwargs):
    generate_slug(instance, sender, "name")


@receiver(post_save, sender=GalleryItem)
def gallery_item_video_signal(sender, instance: GalleryItem, created: bool, **kwargs):
    if instance.item_type != GalleryItem.ItemType.VIDEO:
        return

    if not instance.original_video:
        return
    if _video_changed(instance):
        return

    from apps.gallery.infrastructure.tasks import process_video_to_hls
    process_video_to_hls.delay(instance.pk)
    print(f"Object {instance.pk} - HLS done")


def _video_changed(instance: GalleryItem) -> bool:
    try:
        old = GalleryItem.objects.only("original_video").get(pk=instance.pk)
        return old.original_video.name != instance.original_video.name
    except GalleryItem.DoesNotExist:
        return True


for model in [Gallery, GalleryItem]:
    connect_media_cleanup(model)
