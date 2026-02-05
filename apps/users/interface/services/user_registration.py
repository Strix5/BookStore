from typing import Optional
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.users.interface.services.profile import ProfileService
from apps.users.interface.tasks import send_verification_email_task


User = get_user_model()


class UserRegistrationService:
    """
    Сервис для регистрации новых пользователей.

    Инкапсулирует всю логику создания пользователя:
    - Создание учетной записи
    - Отправка верификационного письма
    - Опциональное создание профиля

    Используется для соблюдения принципа "толстые модели, тонкие контроллеры".
    """

    @staticmethod
    @transaction.atomic
    def register_user(
            *,
            email: str,
            nickname: str,
            first_name: str,
            last_name: str,
            password: str,
            age: int,
            profile_data: Optional[dict] = None,
            domain: str,
            scheme: str = "https"
    ) -> User:
        """
        Регистрирует нового пользователя в системе.

        Args:
            email: Email пользователя (используется как USERNAME_FIELD)
            nickname: Уникальный никнейм
            first_name: Имя
            last_name: Фамилия
            age: Age
            password: Пароль (будет хеширован)
            profile_data: Опциональные данные профиля (биография, аватар)
            domain: Домен для генерации ссылки верификации
            scheme: Схема URL (http/https)

        Returns:
            Созданный пользователь с is_active=False

        Raises:
            ValueError: Если обязательные поля не заполнены
            IntegrityError: Если email или nickname уже существуют
        """
        user = User.objects.create(
            email=email,
            nickname=nickname,
            first_name=first_name,
            last_name=last_name,
            age=age,
        )
        user.set_password(password)
        user.is_active = False
        user.save(update_fields=["password", "is_active"])

        if profile_data:
            ProfileService.create_profile(user=user, **profile_data)

        transaction.on_commit(
            lambda: send_verification_email_task(
                user_id=user.id,
                domain=domain,
                scheme=scheme
            )
        )

        return user
