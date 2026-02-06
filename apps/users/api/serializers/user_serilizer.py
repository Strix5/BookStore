from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.api.serializers.profile_serializer import ProfileSerializer
from apps.users.interface.services import (ProfileService,
                                           UserRegistrationService,
                                           UserService)

User = get_user_model()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "nickname", "first_name", "last_name", "age"]
        read_only_fields = ("id", "email")

    def update(self, instance, validated_data):
        return UserService.update_user(user=instance, **validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False, write_only=True)
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, help_text="Min 8 symbols"
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
            "age": {"required": True},
        }

    def validate_password(self, value: str) -> str:
        if len(value) < 8:
            raise serializers.ValidationError("Min 8 symbols.")
        return value

    def create(self, validated_data):
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
            scheme=scheme,
        )

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", serializers.empty)

        user = UserService.update_user(
            user=instance,
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            nickname=validated_data.get("nickname"),
            age=validated_data.get("age"),
        )

        self._handle_profile_update(user, profile_data)

        return user

    def _handle_profile_update(self, user: User, profile_data) -> None:
        if profile_data is serializers.empty:
            return

        if profile_data is None:
            if hasattr(user, "profile"):
                ProfileService.delete_profile(user.profile)
            return

        if hasattr(user, "profile"):
            ProfileService.update_profile(user.profile, **profile_data)
        else:
            ProfileService.create_profile(user=user, **profile_data)

    @staticmethod
    def _get_domain_and_scheme(request) -> tuple[str, str]:
        """
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
