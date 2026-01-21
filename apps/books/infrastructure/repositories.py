from typing import Iterable

from apps.books.common import BookRepositoryABC
from apps.books.infrastructure.selectors import get_active_books_for_entity
from apps.books.domain.entities import BookEntity


class BookRepository(BookRepositoryABC):
    def get_active_books(self) -> Iterable[BookEntity]:
        qs = get_active_books_for_entity()

        for book in qs:
            yield BookEntity(
                id=book.id,
                is_adult=book.is_adult
            )
