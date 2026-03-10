from django.conf import settings
from rest_framework import serializers

from apps.galleries.infrastructure.models import Gallery, GalleryItem
from commons.interfaces.urlfile_path import FileResponseField


class HLSQualitySerializer(serializers.Serializer):
    master = serializers.SerializerMethodField()
    q480p = serializers.SerializerMethodField()
    q720p = serializers.SerializerMethodField()
    q1080p = serializers.SerializerMethodField()

    def _media_url(self, relative_path: str) -> str:
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"{settings.MEDIA_URL}{relative_path}")
        return f"{settings.MEDIA_URL}{relative_path}"

    def _quality_url(self, obj: GalleryItem, quality_name: str) -> str | None:
        """
        Вычисляет URL плейлиста одного качества по пути master.m3u8.
        master.m3u8 лежит в .../hls/{item_id}/master.m3u8,
        качества — в .../hls/{item_id}/480p/index.m3u8.
        """
        if not obj.is_video_ready:
            return None
        # Берём директорию master.m3u8 и добавляем подпапку качества
        master_dir = obj.hls_master_playlist.name.rsplit("/", 1)[0]
        return self._media_url(f"{master_dir}/{quality_name}/index.m3u8")

    def get_master(self, obj: GalleryItem) -> str | None:
        if not obj.is_video_ready:
            return None
        return self._media_url(obj.hls_master_playlist.name)

    def get_q480p(self, obj: GalleryItem) -> str | None:
        return self._quality_url(obj, "480p")

    def get_q720p(self, obj: GalleryItem) -> str | None:
        return self._quality_url(obj, "720p")

    def get_q1080p(self, obj: GalleryItem) -> str | None:
        return self._quality_url(obj, "1080p")


class GalleryItemSerializer(serializers.ModelSerializer):
    """
    Сериализует один медиафайл. Поле hls присутствует всегда, но заполнено
    только когда item_type=video и hls_status=ready.

    Зачем image_url вместо image (ImageField напрямую):
    ImageField по умолчанию возвращает относительный путь вида /media/galleries/images/...
    SerializerMethodField строит абсолютный URL через request.build_absolute_uri —
    клиент получает готовую ссылку без дополнительной обработки.
    """

    image = FileResponseField()
    hls = serializers.SerializerMethodField()

    class Meta:
        model = GalleryItem
        fields = (
            "id", "item_type", "order",
            "image",
            "hls_status", "hls",
        )

    def get_hls(self, obj: GalleryItem) -> dict | None:
        """
        Возвращает HLS-данные только для видео.
        Передаём context (с request) во вложенный сериализатор —
        он нужен для построения абсолютных URL качеств.
        """
        if obj.item_type != GalleryItem.ItemType.VIDEO:
            return None
        return HLSQualitySerializer(obj, context=self.context).data


class GalleryListSerializer(serializers.ModelSerializer):
    """
    Легкий сериализатор альбома для list-эндпоинта.
    Только мета-данные — без items. Для карточек в ленте.
    """

    name = serializers.CharField()
    cover = FileResponseField()

    class Meta:
        model = Gallery
        fields = ("id", "slug", "name", "cover", "order")


class GalleryDetailSerializer(serializers.ModelSerializer):
    """
    Детальный сериализатор альбома — с описанием и вложенными items.
    Prefetch в selector уже отфильтровал неактивные items,
    поэтому items_data читается из prefetch-кэша без лишних запросов.
    """

    name = serializers.CharField()
    description = serializers.CharField()
    cover = FileResponseField()
    items = GalleryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = ("id", "slug", "name", "description", "cover", "order", "items")
