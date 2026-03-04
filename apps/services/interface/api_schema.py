from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter


response_401 = OpenApiResponse(
    description="Не авторизован. Передайте JWT-токен в заголовке Authorization: Bearer <token>.",
)

response_404_service_group = OpenApiResponse(
    description="Группа сервисов не найдена или неактивна.",
    response={"type": "object", "properties": {"detail": {"type": "string"}}},
    examples=[OpenApiExample(name="Не найдено", value={"detail": "Not found."})],
)

response_404_service = OpenApiResponse(
    description="Сервис не найден или неактивен.",
    response={"type": "object", "properties": {"detail": {"type": "string"}}},
    examples=[OpenApiExample(name="Не найдено", value={"detail": "Not found."})],
)


service_group_slug_path = OpenApiParameter(
    name="slug",
    location=OpenApiParameter.PATH,
    description="Уникальный slug группы сервисов.",
    required=True,
    type=OpenApiTypes.STR,
    examples=[OpenApiExample(name="Пример", value="benefits")],
)

service_slug_path = OpenApiParameter(
    name="slug",
    location=OpenApiParameter.PATH,
    description="Уникальный slug сервиса.",
    required=True,
    type=OpenApiTypes.STR,
    examples=[OpenApiExample(name="Пример", value="bonus-program")],
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


service_group_list_example = OpenApiExample(
    name="Список групп сервисов",
    value={
        "count": 3,
        "total_pages": 1,
        "current_page": 1,
        "next": None,
        "previous": None,
        "results": [
            {"id": 1, "slug": "benefits", "name": "Льготы", "image": None, "order": 0},
            {"id": 2, "slug": "business", "name": "Бизнес", "image": "https://cdn.example.com/service_groups/business.jpg", "order": 1},
        ],
    },
    response_only=True,
)

service_group_detail_example = OpenApiExample(
    name="Детальная группа с сервисами",
    value={
        "id": 1,
        "slug": "benefits",
        "name": "Льготы",
        "description": "Специальные условия для наших клиентов.",
        "image": None,
        "order": 0,
        "services": [
            {"id": 1, "slug": "bonus-program", "name": "Бонусная программа", "image": None, "order": 0},
            {"id": 2, "slug": "discounts", "name": "Скидки", "image": None, "order": 1},
        ],
    },
    response_only=True,
)

service_list_example = OpenApiExample(
    name="Список сервисов группы",
    value={
        "count": 2,
        "total_pages": 1,
        "current_page": 1,
        "next": None,
        "previous": None,
        "results": [
            {"id": 1, "slug": "bonus-program", "name": "Бонусная программа", "image": None, "order": 0},
            {"id": 2, "slug": "discounts", "name": "Скидки", "image": None, "order": 1},
        ],
    },
    response_only=True,
)

service_detail_example = OpenApiExample(
    name="Детальный сервис",
    value={
        "id": 1,
        "slug": "bonus-program",
        "name": "Бонусная программа",
        "description": "Накапливайте баллы с каждой покупки.",
        "image": "https://cdn.example.com/services/bonus.jpg",
        "order": 0,
        "group_slug": "benefits",
    },
    response_only=True,
)


service_group_list_schema = {
    "summary": "Список групп сервисов",
    "description": (
        "Возвращает постраничный список активных групп сервисов. "
        "Без вложенных сервисов — для отрисовки меню верхнего уровня."
    ),
    "parameters": pagination_params,
    "responses": {
        200: OpenApiResponse(description="Список групп.", examples=[service_group_list_example]),
        401: response_401,
    },
}

service_group_retrieve_schema = {
    "summary": "Детальная группа сервисов",
    "description": (
        "Возвращает группу по slug со всеми вложенными активными сервисами."
    ),
    "parameters": [service_group_slug_path],
    "responses": {
        200: OpenApiResponse(description="Группа с сервисами.", examples=[service_group_detail_example]),
        401: response_401,
        404: response_404_service_group,
    },
}

service_group_services_schema = {
    "summary": "Сервисы конкретной группы",
    "description": (
        "Постраничный список активных сервисов, принадлежащих группе с указанным slug."
    ),
    "parameters": [service_group_slug_path, *pagination_params],
    "responses": {
        200: OpenApiResponse(description="Список сервисов группы.", examples=[service_list_example]),
        401: response_401,
        404: response_404_service_group,
    },
}

service_list_schema = {
    "summary": "Список всех сервисов",
    "description": "Плоский постраничный список всех активных сервисов без группировки.",
    "parameters": pagination_params,
    "responses": {
        200: OpenApiResponse(description="Список сервисов.", examples=[service_list_example]),
        401: response_401,
    },
}

service_retrieve_schema = {
    "summary": "Детальный сервис",
    "description": "Возвращает полную информацию о сервисе по slug.",
    "parameters": [service_slug_path],
    "responses": {
        200: OpenApiResponse(description="Детальная информация о сервисе.", examples=[service_detail_example]),
        401: response_401,
        404: response_404_service,
    },
}