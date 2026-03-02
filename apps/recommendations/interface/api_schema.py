from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)


response_401 = OpenApiResponse(
    description="Не авторизован. Передайте JWT-токен в заголовке Authorization: Bearer <token>.",
)

response_404_recommendation = OpenApiResponse(
    description="Рекомендация не найдена или неактивна.",
    response={
        "type": "object",
        "properties": {
            "detail": {"type": "string"},
        },
    },
    examples=[
        OpenApiExample(
            name="Не найдено",
            value={"detail": "Not found."},
        ),
    ],
)

recommendation_slug_path = OpenApiParameter(
    name="slug",
    location=OpenApiParameter.PATH,
    description="Уникальный slug рекомендации.",
    required=True,
    type=OpenApiTypes.STR,
    examples=[
        OpenApiExample(name="Пример", value="top-10-books-of-2024"),
    ],
)

pagination_params = [
    OpenApiParameter(
        name="page",
        location=OpenApiParameter.QUERY,
        description="Номер страницы.",
        required=False,
        type=OpenApiTypes.INT,
        examples=[OpenApiExample(name="Первая страница", value=1)],
    ),
    OpenApiParameter(
        name="per_page",
        location=OpenApiParameter.QUERY,
        description="Количество элементов на странице (максимум 100).",
        required=False,
        type=OpenApiTypes.INT,
        examples=[OpenApiExample(name="12 элементов", value=12)],
    ),
]

recommendation_list_example = OpenApiExample(
    name="Список рекомендаций",
    value={
        "count": 42,
        "total_pages": 4,
        "current_page": 1,
        "next": "https://api.example.com/recommendations/?page=2",
        "previous": None,
        "results": [
            {
                "id": 1,
                "slug": "top-10-books-of-2024",
                "title": "Топ-10 книг 2024 года",
                "image": "https://cdn.example.com/recommendations/top10.jpg",
                "created_at": "2024-01-15",
                "is_active": True,
            }
        ],
    },
    response_only=True,
)

recommendation_detail_example = OpenApiExample(
    name="Детальная рекомендация",
    value={
        "id": 1,
        "slug": "top-10-books-of-2024",
        "title": "Топ-10 книг 2024 года",
        "description": "Лучшие книги по мнению наших редакторов.",
        "image": "https://cdn.example.com/recommendations/top10.jpg",
        "created_at": "2024-01-15",
        "is_active": True,
        "books": [
            {
                "book_slug": "clean-code",
                "book_name": "Чистый код",
                "book_image": "https://cdn.example.com/books/clean-code.jpg",
                "order": 1,
            },
            {
                "book_slug": "the-pragmatic-programmer",
                "book_name": "Программист-прагматик",
                "book_image": None,
                "order": 2,
            },
        ],
    },
    response_only=True,
)

recommendation_list_schema = {
    "summary": "Список рекомендаций",
    "description": (
        "Возвращает постраничный список активных рекомендаций. "
        "Каждый элемент содержит заголовок, slug и обложку — "
        "без вложенных книг (для карточек в ленте)."
    ),
    "parameters": pagination_params,
    "responses": {
        200: OpenApiResponse(
            description="Постраничный список рекомендаций.",
            examples=[recommendation_list_example],
        ),
        401: response_401,
    },
}

recommendation_retrieve_schema = {
    "summary": "Детальная рекомендация",
    "description": (
        "Возвращает полную информацию о рекомендации по slug: "
        "заголовок, описание, обложку и упорядоченный список книг."
    ),
    "parameters": [recommendation_slug_path],
    "responses": {
        200: OpenApiResponse(
            description="Детальная информация о рекомендации.",
            examples=[recommendation_detail_example],
        ),
        401: response_401,
        404: response_404_recommendation,
    },
}
