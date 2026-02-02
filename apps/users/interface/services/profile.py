from django.db import transaction
from django.contrib.auth import get_user_model

from apps.users.infrastructure.models import Profile


User = get_user_model()


class ProfileService:
    """
    Отвечает за CRUD операции с профилями и связанную бизнес-логику.
    """

    @staticmethod
    def create_profile(user: User, **profile_data) -> Profile:
        """
        Создает профиль для пользователя.

        Args:
            user: Пользователь, для которого создается профиль
            **profile_data: Данные профиля (biography, avatar)

        Returns:
            Созданный профиль

        Raises:
            IntegrityError: Если профиль уже существует
        """
        return Profile.objects.create(user=user, **profile_data)

    @staticmethod
    def get_or_create_profile(user: User, **profile_data) -> tuple[Profile, bool]:
        """
        Получает существующий или создает новый профиль.

        Args:
            user: Пользователь
            **profile_data: Данные профиля (используются только при создании)

        Returns:
            Tuple (профиль, создан ли новый)
        """
        return Profile.objects.get_or_create(user=user, defaults=profile_data)

    @staticmethod
    @transaction.atomic
    def update_profile(profile: Profile, **profile_data) -> Profile:
        """
        Обновляет данные профиля.

        Args:
            profile: Обновляемый профиль
            **profile_data: Новые данные (biography, avatar)

        Returns:
            Обновленный профиль
        """
        for field, value in profile_data.items():
            setattr(profile, field, value)

        profile.save()
        return profile

    @staticmethod
    def delete_profile(profile: Profile) -> None:
        """
        Удаляет профиль пользователя.

        Args:
            profile: Удаляемый профиль
        """
        profile.delete()