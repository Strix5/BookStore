from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.users.api.serializers import ProfileSerializer
from apps.users.infrastructure.models import Profile
from apps.users.infrastructure.permissions import IsOwnerOrAdmin
from apps.users.infrastructure.selectors import get_profile

User = get_user_model()


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = get_profile()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = "pk"

    @action(
        detail=False,
        methods=["get", "delete", "put", "patch"],
        url_path="me",
        url_name="me",
    )
    def me(self, request: Request) -> Response:
        """
        - GET: get profile
        - DELETE: delete profile
        - PUT/PATCH: update profile
        """
        profile = self._get_current_user_profile(request)

        if request.method == "GET":
            return self._handle_get_profile(profile)

        if request.method == "DELETE":
            return self._handle_delete_profile(request, profile)

        return self._handle_update_profile(request, profile)

    @staticmethod
    def _get_current_user_profile(request: Request) -> Profile:
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            raise NotFound(detail="Profile Not Found")

    def _handle_get_profile(self, profile: Profile) -> Response:
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def _handle_delete_profile(self, request: Request, profile: Profile) -> Response:
        self.check_object_permissions(request, profile)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _handle_update_profile(self, request: Request, profile: Profile) -> Response:
        partial = request.method == "PATCH"

        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def create(self, request: Request, *args, **kwargs) -> Response:
        target_user = self._determine_target_user(request)

        if self._profile_exists(target_user):
            return Response(
                {"detail": "Profile already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self._create_profile_for_user(request, target_user)

    def _determine_target_user(self, request: Request) -> User:
        if request.user.is_staff and "user" in request.data:
            return self._get_user_by_id(request.data["user"])

        return request.user

    @staticmethod
    def _get_user_by_id(user_id: int) -> User:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"user": "Not found"})

    @staticmethod
    def _profile_exists(user: User) -> bool:
        return hasattr(user, "profile") and user.profile is not None

    def _create_profile_for_user(self, request: Request, target_user: User) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                serializer.save(user=target_user)
        except IntegrityError:
            return Response(
                {"detail": "Race or integrity error"}, status=status.HTTP_409_CONFLICT
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @transaction.atomic
    def update(self, request: Request, *args, **kwargs) -> Response:
        return self._perform_update(request, partial=False)

    @transaction.atomic
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        return self._perform_update(request, partial=True)

    def _perform_update(self, request: Request, partial: bool) -> Response:
        profile = self.get_object()
        self.check_object_permissions(request, profile)

        serializer = self.get_serializer(profile, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        profile = self.get_object()
        self.check_object_permissions(request, profile)
        profile.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
