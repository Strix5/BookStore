from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.infrastructure.models import Profile
from apps.users.interface.services import ProfileService

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "email", "nickname", "first_name", "last_name", "age")
        read_only_fields = ("id", "email")


class ProfileSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "user", "biography", "avatar")
        read_only_fields = ("id", "user")

    def update(self, instance, validated_data):
        return ProfileService.update_profile(profile=instance, **validated_data)
