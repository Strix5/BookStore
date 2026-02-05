from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.infrastructure.models import Profile
from apps.users.interface.services import ProfileService

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Публичное представление пользователя.

    Используется для отображения информации о пользователе
    без конфиденциальных данных (пароль, email для неавторизованных и т.д.).
    """

    class Meta:
        model = User
        fields = ("id", "email", "nickname", "first_name", "last_name", "age")
        read_only_fields = ("id", "email")


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя.

    Принцип: сериализатор не изменяет связанного пользователя,
    только данные профиля (biography, avatar).
    """

    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "user", "biography", "avatar")
        read_only_fields = ("id", "user")

    def update(self, instance, validated_data):
        """
        Обновление профиля через сервисный слой.

        Делегируем логику обновления сервису для централизации
        бизнес-правил и возможности повторного использования.
        """
        return ProfileService.update_profile(profile=instance, **validated_data)
