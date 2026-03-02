from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter

from apps.favorites.api.serializers import (
    FavoriteSerializer,
    AddToFavoritesSerializer,
    ToggleFavoriteSerializer
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


favorite_list_schema = {
    "tags": ["Favorites"],
    "summary": "Список избранных книг",
    "description": (
        "Возвращает все книги пользователя из избранного, "
        "отсортированные по дате добавления (новые первые). "
        "Пустой массив если избранного нет."
    ),
    "responses": {
        200: OpenApiResponse(
            response=FavoriteSerializer(many=True),
            description="Список избранного.",
            examples=[
                OpenApiExample(
                    name="Непустое избранное",
                    value=[
                        {
                            "id": 1,
                            "book": {
                                "id": 5,
                                "name": "Clean Code",
                                "slug": "clean-code",
                                "price": 500,
                            },
                            "created_at": "2026-01-01T10:00:00Z",
                        }
                    ],
                ),
                OpenApiExample(name="Пустое избранное", value=[]),
            ],
        ),
        401: response_401,
    },
}

favorite_add_schema = {
    "tags": ["Favorites"],
    "summary": "Добавить книгу в избранное",
    "description": (
        "Добавляет книгу в избранное. "
        "Идемпотентен: повторный вызов с той же книгой возвращает 200 без ошибки."
    ),
    "request": AddToFavoritesSerializer,
    "responses": {
        201: OpenApiResponse(
            response=FavoriteSerializer,
            description="Книга добавлена в избранное.",
            examples=[
                OpenApiExample(
                    name="Добавлено",
                    value={
                        "message": "Added to favorites",
                        "favorite": {
                            "id": 1,
                            "book": {"id": 5, "name": "Clean Code", "price": 500},
                            "created_at": "2026-01-01T10:00:00Z",
                        },
                    },
                ),
            ],
        ),
        200: OpenApiResponse(
            response=FavoriteSerializer,
            description="Книга уже была в избранном.",
            examples=[
                OpenApiExample(
                    name="Уже в избранном",
                    value={
                        "message": "Already in favorites",
                        "favorite": {
                            "id": 1,
                            "book": {"id": 5, "name": "Clean Code", "price": 500},
                            "created_at": "2026-01-01T08:00:00Z",
                        },
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Книга не найдена или неактивна.",
            examples=[
                OpenApiExample(
                    name="Не найдена",
                    value={"book_id": ["Book not found or inactive"]},
                ),
            ],
        ),
        401: response_401,
    },
}

favorite_remove_schema = {
    "tags": ["Favorites"],
    "summary": "Удалить книгу из избранного",
    "description": "Удаляет конкретную книгу из избранного пользователя.",
    "parameters": [book_id_path],
    "responses": {
        204: OpenApiResponse(
            description="Книга удалена из избранного.",
            examples=[
                OpenApiExample(
                    name="Удалено",
                    value={"message": "Removed from favorites"},
                ),
            ],
        ),
        401: response_401,
        404: response_404_favorites,
    },
}

favorite_toggle_schema = {
    "tags": ["Favorites"],
    "summary": "Переключить статус избранного",
    "description": (
        "Добавляет книгу в избранное если её там нет, удаляет если есть. "
        "Удобно для кнопки «♥»: один запрос вместо check + add/remove."
    ),
    "request": ToggleFavoriteSerializer,
    "responses": {
        200: OpenApiResponse(
            description="Статус переключён. is_favorite отражает текущее состояние.",
            examples=[
                OpenApiExample(
                    name="Добавлено через toggle",
                    value={"message": "Book added", "is_favorite": True},
                ),
                OpenApiExample(
                    name="Удалено через toggle",
                    value={"message": "Book removed", "is_favorite": False},
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Книга не найдена или неактивна.",
            examples=[
                OpenApiExample(
                    name="Не найдена",
                    value={"book_id": ["Book not found or inactive"]},
                ),
            ],
        ),
        401: response_401,
     },
}

favorite_clear_schema = {
    "tags": ["Favorites"],
    "summary": "Очистить всё избранное",
    "description": "Удаляет все книги из избранного пользователя.",
    "responses": {
        200: OpenApiResponse(
            description="Избранное очищено.",
            examples=[
                OpenApiExample(
                    name="Очищено",
                    value={"message": "Favorites cleared", "deleted_count": 5},
                ),
                OpenApiExample(
                    name="Было пустым",
                    value={"message": "Favorites cleared", "deleted_count": 0},
                ),
            ],
        ),
        401: response_401,
    },
}

favorite_check_schema = {
    "tags": ["Favorites"],
    "summary": "Проверить наличие книги в избранном",
    "description": (
        "Быстрая булева проверка: есть ли книга в избранном. "
        "Используется для отображения статуса «♥» на карточках "
        "без загрузки всего списка избранного."
    ),
    "parameters": [book_id_path],
    "responses": {
        200: OpenApiResponse(
            description="Результат проверки.",
            examples=[
                OpenApiExample(name="В избранном", value={"is_favorite": True}),
                OpenApiExample(name="Не в избранном", value={"is_favorite": False}),
            ],
        ),
        401: response_401,
    },
}
