from dataclasses import dataclass


@dataclass(frozen=True)
class BookEntity:
    id: int
    is_adult: bool

    def is_allowed_for_age(self, age) -> bool:
        return self.is_adult and age > 18 or not self.is_adult
