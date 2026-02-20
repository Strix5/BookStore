from rest_framework import serializers

from apps.orders.infrastructure.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    book_slug = serializers.SlugRelatedField(
        source="book",
        read_only=True,
        slug_field="slug",
    )
    book_name = serializers.CharField(source="book.name")
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "book_slug",
            "book_name",
            "quantity",
            "price",
            "total_price",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total_price",
            "items",
            "created_at",
            "created_at_display",
        )

    def get_created_at_display(self, obj) -> str:
        return obj.created_at.strftime("%H:%M %d.%m.%Y")
