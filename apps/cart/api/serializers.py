from rest_framework import serializers

from apps.books.infrastructure.models import Book
from apps.cart.infrastructure.models import Cart, CartItem, Favorite
from apps.books.api.serializers import BookListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'book',
            'quantity',
            'subtotal',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    @staticmethod
    def get_subtotal(obj: CartItem) -> float:
        return obj.book.price * obj.quantity

    def to_representation(self, instance: CartItem) -> dict:
        representation = super().to_representation(instance)
        request = self.context.get('request')
        book_serializer = BookListSerializer(
            instance.book,
            context={'request': request}
        )
        representation['book'] = book_serializer.data
        return representation


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total_items',
            'total_price',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_items(self, obj: Cart) -> int:
        return obj.total_items

    def get_total_price(self, obj: Cart) -> float:
        return sum(item.subtotal for item in obj.items.all())


class AddToCartSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(
        min_value=0,
        help_text="ID книги для добавления в корзину"
    )
    quantity = serializers.IntegerField(
        default=1,
        min_value=1,
        max_value=999,
        help_text="Количество книг (от 1 до 999)"
    )

    def validate_book_id(self, value: int) -> int:
        if not Book.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError(
                "Book not found or inactive"
            )

        return value

    def validate(self, attrs: dict) -> dict:
        request = self.context.get('request')
        if request and request.user:
            book = Book.objects.get(id=attrs['book_id'])

            user_age = getattr(request.user, 'age', 0)
            if book.is_adult and user_age < 18:
                raise serializers.ValidationError(
                    "You must be 18+ to add this book"
                )

            requested_quantity = attrs.get('quantity', 1)
            if book.in_stock < 1:
                raise serializers.ValidationError(
                    f"'{book.safe_translation_getter('name', any_language=True)}' is out of stock."
                )

            if requested_quantity > book.in_stock:
                raise serializers.ValidationError(
                    f"Only {book.in_stock} copies available, but you requested {requested_quantity}."
                )

        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=0,
        max_value=999,
        help_text="Новое количество (0 для удаления)"
    )


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
