from rest_framework import serializers

from apps.books.infrastructure.models import Book
from apps.favorites.infrastructure.models import Favorite
from apps.books.api.serializers import BookListSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = [
            'id',
            'book',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AddToFavoritesSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(
        min_value=1,
        help_text="ID книги для добавления в избранное"
    )

    def validate_book_id(self, value: int) -> int:
        if not Book.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError(
                "Book not found or inactive"
            )

        return value


class ToggleFavoriteSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(
        min_value=1,
        help_text="ID книги"
    )

    def validate_book_id(self, value: int) -> int:
        if not Book.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError(
                "Book not found or inactive"
            )

        return value
