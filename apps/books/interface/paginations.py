from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BaseCustomPagination(PageNumberPagination):
    page_size_query_param = "per_page"
    max_page_size = 100

    def get_paginated_response(self, data: list[Any]) -> Response:
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "example": 123},
                "total_pages": {"type": "integer", "example": 12},
                "current_page": {"type": "integer", "example": 1},
                "next": {"type": "string", "format": "uri", "nullable": True},
                "previous": {"type": "string", "format": "uri", "nullable": True},
                "results": schema,
            },
            "required": ["count", "results"],
        }


class CustomPagination(BaseCustomPagination):
    page_size = 12