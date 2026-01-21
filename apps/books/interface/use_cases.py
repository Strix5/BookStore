from typing import Iterable
from apps.books.infrastructure.repositories import BookRepository


class GetAllowedBooksUseCase:

    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository

    def execute(
        self,
        *,
        user_age: int
    ) -> Iterable[int]:
        allowed_ids = []

        for book in self.book_repository.get_active_books():
            if book.is_allowed_for_age(age=user_age):
                allowed_ids.append(book.id)

        return allowed_ids
