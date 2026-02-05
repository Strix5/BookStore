from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class UserService:
    @staticmethod
    @transaction.atomic
    def update_user(user: User, **user_data) -> User:
        """
        Обновляет данные пользователя.

        Args:
            user: Обновляемый пользователь
            **user_data: Новые данные (first_name, last_name, nickname)

        Returns:
            Обновленный пользователь

        Note:
            Email и password обновляются через отдельные методы для безопасности
        """
        allowed_fields = {"first_name", "last_name", "nickname", "age"}

        for field, value in user_data.items():
            if field in allowed_fields:
                setattr(user, field, value)

        user.save()
        return user

    @staticmethod
    def activate_user(user: User) -> None:
        """
        Активирует пользователя после верификации email.

        Args:
            user: Активируемый пользователь
        """
        user.is_active = True
        user.save(update_fields=["is_active"])
