from abc import ABC, abstractmethod
from typing import Iterable
from apps.books.domain.entities import BookEntity


class BookRepositoryABC(ABC):

    @abstractmethod
    def get_active_books(self) -> Iterable[BookEntity]:
        ...
