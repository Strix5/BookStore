from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from commons.models.abstract_models import AbstractDateTimeModel


class Gallery(TranslatableModel, AbstractDateTimeModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True, null=True),
    )
    cover = models.ImageField(
        upload_to="gallery/covers/",
        max_length=255,
        blank=True,
        null=True,
    )

    slug = models.SlugField(unique=True, max_length=255)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Gallery")
        verbose_name_plural = _("Galleries")
        ordering = ("order",)

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True)


class GalleryItem(AbstractDateTimeModel):

    class ItemType(models.TextChoices):
        IMAGE = "image", _("Image")
        VIDEO = "video", _("Video")

    class HLSStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        READY = "ready", _("Ready")
        FAILED = "failed", _("Failed")

    gallery = models.ForeignKey(
        to=Gallery,
        on_delete=models.CASCADE,
        related_name="items",
    )

    item_type = models.CharField(
        max_length=10,
        choices=ItemType.choices,
        default=ItemType.IMAGE,
    )

    image = models.ImageField(
        upload_to="gallery/images/",
        max_length=255,
        blank=True,
        null=True,
    )

    original_video = models.FileField(
        upload_to="gallery/videos/originals/",
        max_length=500,
        blank=True,
        null=True,
        help_text=_("Upload MP4/MOV/AVI. HLS will be generated automatically."),
    )

    # master.m3u8 (480p/720p/1080p).
    hls_master_playlist = models.FileField(
        upload_to="gallery/videos/hls/",
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("HLS Master Playlist (.m3u8)"),
    )

    hls_status = models.CharField(
        max_length=15,
        choices=HLSStatus.choices,
        default=HLSStatus.PENDING,
        verbose_name=_("HLS Status"),
    )

    hls_error = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("HLS Error"),
        help_text=_("Filled in if HLS conversion failed."),
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Gallery Item")
        verbose_name_plural = _("Gallery Items")
        ordering = ("order",)

    def __str__(self) -> str:
        return f"{self.gallery} — {self.item_type} #{self.pk}"

    @property
    def is_video_ready(self) -> bool:
        return self.hls_status == self.HLSStatus.READY and bool(self.hls_master_playlist)
