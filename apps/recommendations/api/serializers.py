from rest_framework import serializers

from apps.recommendations.infrastructure.models import Recommendation, RecommendationBook
from commons.interfaces.urlfile_path import FileResponseField


class RecommendationBookSerializer(serializers.ModelSerializer):
    book_slug = serializers.SlugField(source="book.slug", read_only=True)

    book_name = serializers.SerializerMethodField()
    book_image = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationBook
        fields = ("book_slug", "book_name", "book_image", "order")

    def get_book_name(self, obj: RecommendationBook) -> str | None:
        return obj.book.safe_translation_getter("name", any_language=True)

    def get_book_image(self, obj: RecommendationBook) -> str | None:
        request = self.context.get("request")
        image = obj.book.image or None
        if image:
            return request.build_absolute_uri(image.url)
        return None


class RecommendationListSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    image = FileResponseField()

    class Meta:
        model = Recommendation
        fields = (
            "id",
            "title",
            "image",
            "slug",
            "created_at",
            "is_active"
        )


class RecommendationDetailSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    description = serializers.CharField()
    image = FileResponseField()

    books = RecommendationBookSerializer(
        source="recommendation_books",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Recommendation
        fields = (
            "id",
            "title",
            "description",
            "image",
            "books",
            "slug",
            "created_at",
            "is_active"
        )
