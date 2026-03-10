from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter

# ──────────────────────────────────────────────
# Переиспользуемые ответы
# ──────────────────────────────────────────────

response_401 = OpenApiResponse(
    description="Не авторизован. Передайте JWT-токен в заголовке Authorization: Bearer <token>.",
)

response_404_gallery = OpenApiResponse(
    description="Альбом не найден или неактивен.",
    response={"type": "object", "properties": {"detail": {"type": "string"}}},
    examples=[OpenApiExample(name="Не найдено", value={"detail": "Not found."})],
)

# ──────────────────────────────────────────────
# Переиспользуемые параметры
# ──────────────────────────────────────────────

gallery_slug_path = OpenApiParameter(
    name="slug",
    location=OpenApiParameter.PATH,
    description="Уникальный slug альбома.",
    required=True,
    type=OpenApiTypes.STR,
    examples=[OpenApiExample(name="Пример", value="book-fair-2024")],
)

pagination_params = [
    OpenApiParameter(
        name="page", location=OpenApiParameter.QUERY,
        description="Номер страницы.", required=False, type=OpenApiTypes.INT,
        examples=[OpenApiExample(name="Первая", value=1)],
    ),
    OpenApiParameter(
        name="per_page", location=OpenApiParameter.QUERY,
        description="Количество элементов на странице (максимум 100).",
        required=False, type=OpenApiTypes.INT,
        examples=[OpenApiExample(name="12 элементов", value=12)],
    ),
]

# ──────────────────────────────────────────────
# Примеры ответов
# ──────────────────────────────────────────────

_hls_example = {
    "master": "https://cdn.example.com/media/gallery/videos/hls/5/master.m3u8",
    "q480p":  "https://cdn.example.com/media/gallery/videos/hls/5/480p/index.m3u8",
    "q720p":  "https://cdn.example.com/media/gallery/videos/hls/5/720p/index.m3u8",
    "q1080p": "https://cdn.example.com/media/gallery/videos/hls/5/1080p/index.m3u8",
}

gallery_list_example = OpenApiExample(
    name="Список альбомов",
    value={
        "count": 8, "total_pages": 1, "current_page": 1,
        "next": None, "previous": None,
        "results": [
            {"id": 1, "slug": "book-fair-2024", "name": "Книжная ярмарка 2024",
             "cover_url": "https://cdn.example.com/media/gallery/covers/fair.jpg", "order": 0},
        ],
    },
    response_only=True,
)

gallery_detail_example = OpenApiExample(
    name="Детальный альбом",
    value={
        "id": 1, "slug": "book-fair-2024", "name": "Книжная ярмарка 2024",
        "description": "Фотографии и видео с нашего стенда.",
        "cover_url": "https://cdn.example.com/media/gallery/covers/fair.jpg",
        "order": 0,
        "items": [
            {"id": 3, "item_type": "image", "order": 0,
             "image_url": "https://cdn.example.com/media/gallery/images/photo1.jpg",
             "hls_status": "pending", "hls": None},
            {"id": 5, "item_type": "video", "order": 1,
             "image_url": None, "hls_status": "ready", "hls": _hls_example},
            {"id": 6, "item_type": "video", "order": 2,
             "image_url": None, "hls_status": "processing", "hls": {
                 "master": None, "q480p": None, "q720p": None, "q1080p": None}},
        ],
    },
    response_only=True,
)

gallery_items_example = OpenApiExample(
    name="Постраничные items",
    value={
        "count": 12, "total_pages": 1, "current_page": 1,
        "next": None, "previous": None,
        "results": [
            {"id": 3, "item_type": "image", "order": 0,
             "image_url": "https://cdn.example.com/media/gallery/images/photo1.jpg",
             "hls_status": "pending", "hls": None},
            {"id": 5, "item_type": "video", "order": 1,
             "image_url": None, "hls_status": "ready", "hls": _hls_example},
        ],
    },
    response_only=True,
)

# ──────────────────────────────────────────────
# Финальные схемы для @extend_schema
# ──────────────────────────────────────────────

gallery_list_schema = {
    "summary": "Список альбомов галереи",
    "description": "Постраничный список активных альбомов без вложенных медиафайлов.",
    "parameters": pagination_params,
    "responses": {
        200: OpenApiResponse(description="Список альбомов.", examples=[gallery_list_example]),
        401: response_401,
    },
}

gallery_retrieve_schema = {
    "summary": "Детальный альбом",
    "description": (
        "Альбом по slug со всеми активными медиафайлами. "
        "Для видео поле `hls` содержит ссылки на master.m3u8 и отдельные качества "
        "(480p/720p/1080p). Пока видео обрабатывается — `hls_status: processing`, "
        "ссылки равны null."
    ),
    "parameters": [gallery_slug_path],
    "responses": {
        200: OpenApiResponse(description="Детальный альбом.", examples=[gallery_detail_example]),
        401: response_401,
        404: response_404_gallery,
    },
}

gallery_items_schema = {
    "summary": "Медиафайлы альбома (постранично)",
    "description": "Постраничный список активных items альбома. Удобен при большом количестве файлов.",
    "parameters": [gallery_slug_path, *pagination_params],
    "responses": {
        200: OpenApiResponse(description="Постраничные items.", examples=[gallery_items_example]),
        401: response_401,
        404: response_404_gallery,
    },
}