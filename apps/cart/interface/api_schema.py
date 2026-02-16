from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter


response_401 = OpenApiResponse(
    description="Не авторизован. Передайте JWT-токен в заголовке Authorization: Bearer <token>.",
)

response_400_stock = OpenApiResponse(
    description="Нарушение бизнес-правила: превышение склада, контент 18+ или невалидные данные.",
    response={
        "type": "object",
        "properties": {
            "error": {"type": "array", "items": {"type": "string"}},
        },
    },
    examples=[
        OpenApiExample(
            name="Нет на складе",
            value={"error": ["'Clean Code' is out of stock."]},
        ),
        OpenApiExample(
            name="Превышение остатка",
            value={"error": ["Only 2 copies of 'Clean Code' available."]},
        ),
        OpenApiExample(
            name="Ограничение по возрасту",
            value={"error": ["You must be 18+ to add this book"]},
        ),
    ],
)

response_404_cart = OpenApiResponse(
    description="Книга не найдена в корзине пользователя.",
    response={"type": "object", "properties": {"error": {"type": "string"}}},
    examples=[
        OpenApiExample(name="Не в корзине", value={"error": "Book 5 not found in cart"}),
    ],
)

response_404_favorites = OpenApiResponse(
    description="Книга не найдена в избранном пользователя.",
    response={"type": "object", "properties": {"error": {"type": "string"}}},
    examples=[
        OpenApiExample(name="Не в избранном", value={"error": "Not in favorites"}),
    ],
)


# Параметр {book_id} в URL-пути — используется в нескольких action-ах.
book_id_path = OpenApiParameter(
    name="book_id",
    location=OpenApiParameter.PATH,
    description="ID книги.",
    required=True,
    type=OpenApiTypes.INT,
    examples=[OpenApiExample(name="Пример", value=5)],
)