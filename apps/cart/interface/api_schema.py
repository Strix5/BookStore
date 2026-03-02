from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter

from apps.cart.api.serializers import (
    CartSerializer,
    AddToCartSerializer,
    CartItemSerializer,
    UpdateCartItemSerializer
)


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


cart_list_schema = {
    "tags": ["Cart"],
    "summary": "Получить корзину",
    "description": (
        "Возвращает корзину пользователя со всеми позициями, "
        "количеством и итоговой стоимостью. "
        "Если корзина пуста или не создана — возвращает объект с пустым списком."
    ),
    "responses": {
        200: OpenApiResponse(
            response=CartSerializer,
            description="Корзина пользователя.",
            examples=[
                OpenApiExample(
                    name="Корзина с товарами",
                    value={
                        "id": 1,
                        "items": [
                            {
                                "id": 3,
                                "book": {
                                    "id": 5,
                                    "name": "Clean Code",
                                    "slug": "clean-code",
                                    "price": 500,
                                    "in_stock": 10,
                                },
                                "quantity": 2,
                                "subtotal": 1000,
                                "created_at": "2026-01-01T10:00:00Z",
                                "updated_at": "2026-01-01T11:00:00Z",
                            }
                        ],
                        "total_items": 2,
                        "total_price": 1000,
                        "created_at": "2026-01-01T10:00:00Z",
                        "updated_at": "2026-01-01T11:00:00Z",
                    },
                ),
                OpenApiExample(
                    name="Пустая корзина",
                    value={
                        "id": None,
                        "items": [],
                        "total_items": 0,
                        "total_price": 0,
                    },
                ),
            ],
        ),
        401: response_401,
    }
}

cart_add_schema = {
    "tags": ["Cart"],
    "summary": "Добавить книгу в корзину",
    "description": (
        "Добавляет книгу в корзину. "
        "Если книга уже есть в корзине — увеличивает quantity. "
        "Проверяет: существование и активность книги, возраст 18+, наличие на складе."
    ),
    "request": AddToCartSerializer,
    "responses": {
        201: OpenApiResponse(
            response=CartItemSerializer,
            description="Книга добавлена в корзину впервые.",
            examples=[
                OpenApiExample(
                    name="Добавлена новая позиция",
                    value={
                        "message": "Item added to cart",
                        "item": {
                            "id": 3,
                            "book": {"id": 5, "name": "Clean Code", "price": 500},
                            "quantity": 2,
                            "subtotal": 1000,
                            "created_at": "2026-01-01T10:00:00Z",
                            "updated_at": "2026-01-01T11:00:00Z",
                        },
                    },
                ),
            ],
        ),
        200: OpenApiResponse(
            response=CartItemSerializer,
            description="Книга уже была в корзине — quantity увеличен.",
            examples=[
                OpenApiExample(
                    name="Количество увеличено",
                    value={
                        "message": "Quantity updated",
                        "item": {
                            "id": 3,
                            "book": {"id": 5, "name": "Clean Code", "price": 500},
                            "quantity": 4,
                            "subtotal": 2000,
                            "created_at": "2026-01-01T10:00:00Z",
                            "updated_at": "2026-01-01T11:00:00Z",
                        },
                    },
                ),
            ],
        ),
        400: response_400_stock,
        401: response_401,
    },
}

cart_patch_schema = {
    "tags": ["Cart"],
    "summary": "Обновить количество книги в корзине",
    "description": (
        "Устанавливает новое количество для позиции. "
        "quantity=0 удаляет позицию из корзины. "
        "Нельзя установить количество больше остатка на складе."
    ),
    "parameters":[book_id_path],
    "request": UpdateCartItemSerializer,
    "responses": {
        200: OpenApiResponse(
            response=CartItemSerializer,
            description="Количество обновлено.",
            examples=[
                OpenApiExample(
                    name="Обновлено",
                    value={
                        "message": "Quantity updated",
                        "item": {
                            "id": 3,
                            "book": {"id": 5, "name": "Clean Code", "price": 500},
                            "quantity": 5,
                            "subtotal": 2500,
                            "created_at": "2026-01-01T10:00:00Z",
                            "updated_at": "2026-01-01T11:00:00Z",
                        },
                    },
                ),
            ],
        ),
        204: OpenApiResponse(
            description="Позиция удалена из корзины (quantity=0).",
            examples=[
                OpenApiExample(
                    name="Удалено через quantity=0",
                    value={"message": "Item removed from cart"},
                ),
            ],
        ),
        400: response_400_stock,
        401: response_401,
        404: response_404_cart,
    },
}

cart_remove_schema = {
    "tags": ["Cart"],
    "summary": "Удалить книгу из корзины",
    "description": "Полностью удаляет позицию из корзины независимо от quantity.",
    "parameters":[book_id_path],
    "responses": {
        204: OpenApiResponse(
            description="Позиция успешно удалена.",
            examples=[
                OpenApiExample(
                    name="Удалено",
                    value={"message": "Item removed from cart"},
                ),
            ],
        ),
        401: response_401,
        404: response_404_cart,
    },
}

cart_clear_schema = {
    "tags": ["Cart"],
    "summary": "Очистить корзину",
    "description": (
        "Удаляет все позиции из корзины. "
        "Сам объект Cart сохраняется. "
        "Возвращает количество удалённых позиций."
    ),
    "responses": {
        200: OpenApiResponse(
            description="Корзина очищена.",
            examples=[
                OpenApiExample(
                    name="Очищена",
                    value={"message": "Cart cleared", "deleted_count": 3},
                ),
                OpenApiExample(
                    name="Корзина была пуста",
                    value={"message": "Cart cleared", "deleted_count": 0},
                ),
            ],
        ),
        401: response_401,
    },
}

cart_summary_schema = {
    "tags": ["Cart"],
    "summary": "Сводка по корзине",
    "description": (
        "Возвращает лёгкую сводку: количество позиций и уникальных книг. "
        "Используется для бейджа на иконке корзины. "
        "Не загружает данные книг — значительно быстрее GET /cart/."
    ),
    "responses": {
        200: OpenApiResponse(
            description="Сводка по корзине.",
            examples=[
                OpenApiExample(
                    name="Сводка",
                    value={"total_items": 7, "unique_books": 3},
                ),
                OpenApiExample(
                    name="Пустая корзина",
                    value={"total_items": 0, "unique_books": 0},
                ),
            ],
        ),
        401: response_401,
    },
}
