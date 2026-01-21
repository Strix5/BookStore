from rest_framework import serializers
from apps.books.infrastructure.models import Book, BookCategory


class BookListSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.SerializerMethodField()
    authors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        source="author",
        slug_field="slug"
    )
    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        source="category",
        slug_field="slug"
    )
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id", "name", "description",
            "file", "image", "slug",
            "is_adult", "authors", "categories",
            "created_at", "created_at_display"
        )

    def get_created_at_display(self, obj):
        return obj.created_at.strftime("%H:%M %d.%m.%Y")

    def get_description(self, obj):
        if obj.description:
            return obj.description[:100] + "..."
        return ""


class BookDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    authors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        source="author",
        slug_field="slug"
    )
    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        source="category",
        slug_field="slug"
    )
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id", "name", "description",
            "file", "image", "slug",
            "is_adult", "authors", "categories",
            "created_at", "created_at_display"
        )

    def get_created_at_display(self, obj):
        return obj.created_at.strftime("%H:%M %d.%m.%Y")


class BookCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    books_count = serializers.IntegerField()

    class Meta:
        model = BookCategory
        fields = ("id", "name", "books_count", "slug", "image")
