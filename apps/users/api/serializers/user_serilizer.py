from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.api.serializers.profile_serializer import ProfileSerializer
from apps.users.interface.services import UserRegistrationService, ProfileService, UserService


User = get_user_model()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "nickname", "first_name", "last_name", "age"]
        read_only_fields = ("id", "email")  # Email нельзя изменить

    def update(self, instance, validated_data):
        return UserService.update_user(user=instance, **validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False, write_only=True)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Min 8 symbols"
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "first_name",
            "last_name",
            "age",
            "password",
            "profile",
        ]
        read_only_fields = ("id",)
        extra_kwargs = {
            "email": {"required": True},
            "nickname": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "age": {"required": True}
        }

    def validate_password(self, value: str) -> str:
        if len(value) < 8:
            raise serializers.ValidationError(
                "Min 8 symbols."
            )
        return value

    def create(self, validated_data):
        """
        Создание пользователя через сервисный слой.

        Сериализатор НЕ содержит бизнес-логику - он только:
        1. Валидирует данные
        2. Извлекает домен из контекста
        3. Делегирует создание в UserRegistrationService
        """
        request = self.context.get("request")
        profile_data = validated_data.pop("profile", None)

        domain, scheme = self._get_domain_and_scheme(request)

        user = UserRegistrationService.register_user(
            email=validated_data["email"],
            nickname=validated_data["nickname"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
            age=validated_data["age"],
            profile_data=profile_data,
            domain=domain,
            scheme=scheme
        )

        return user

    def update(self, instance, validated_data):
        """
        Обновление пользователя и профиля.

        Принцип разделения ответственности:
        - UserService обновляет данные пользователя
        - ProfileService управляет профилем
        """
        profile_data = validated_data.pop("profile", serializers.empty)

        # Обновляем данные пользователя
        user = UserService.update_user(
            user=instance,
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            nickname=validated_data.get("nickname"),
            age=validated_data.get("age")
        )

        # Управляем профилем согласно переданным данным
        self._handle_profile_update(user, profile_data)

        return user

    def _handle_profile_update(self, user: User, profile_data) -> None:
        """
        Обработка обновления профиля.

        Три сценария:
        1. profile_data не передан (empty) - не трогаем профиль
        2. profile_data = None - удаляем профиль
        3. profile_data = {...} - обновляем/создаем профиль

        Выделено в отдельный метод для читаемости основного метода update.
        """
        # Если данные профиля не переданы - не трогаем
        if profile_data is serializers.empty:
            return

        # Если явно передан null - удаляем профиль
        if profile_data is None:
            if hasattr(user, "profile"):
                ProfileService.delete_profile(user.profile)
            return

        # Обновляем или создаем профиль
        if hasattr(user, "profile"):
            ProfileService.update_profile(user.profile, **profile_data)
        else:
            ProfileService.create_profile(user=user, **profile_data)

    @staticmethod
    def _get_domain_and_scheme(request) -> tuple[str, str]:
        """
        Извлекает домен и схему из request или настроек.

        Выделено в отдельный метод для:
        - Улучшения читаемости
        - Упрощения тестирования
        - Соблюдения принципа единственной ответственности

        Returns:
            Tuple (domain, scheme)
        """
        if request is not None:
            domain = request.get_host()
            scheme = "https" if request.is_secure() else "http"
        else:
            from django.conf import settings
            domain = getattr(settings, "BACKEND_DOMAIN", "localhost:8000")
            scheme = "http"

        return domain, scheme
