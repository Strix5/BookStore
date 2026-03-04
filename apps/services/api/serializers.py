from rest_framework import serializers

from apps.services.infrastructure.models import ServiceGroup, Service
from commons.interfaces.urlfile_path import FileResponseField


class ServiceListSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.SerializerMethodField()
    image = FileResponseField()

    class Meta:
        model = Service
        fields = ("id", "slug", "name", "image", "order")

    def get_description(self, obj):
        if obj.description:
            return obj.description[:100] + "..."
        return ""


class SerializerDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    image = FileResponseField()

    group_slug = serializers.SlugRelatedField(
        source="group",
        slug_field="slug",
        read_only=True,
    )

    class Meta:
        model = Service
        fields = ("id", "name", "description", "image", "order", "slug", "group_slug")
