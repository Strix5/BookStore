from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import RegisterSerializer, UserUpdateSerializer
from apps.users.interface.services import UserService
from apps.users.interface.tokens import email_verification_token

User = get_user_model()


class VerifyEmailView(APIView):
    """
    Верификация email пользователя по ссылке.

    Принимает GET запрос с параметрами:
    - uidb64: Закодированный ID пользователя
    - token: Токен верификации

    Принцип единственной ответственности: только верификация email.
    """

    # Константы для сообщений - улучшает поддерживаемость
    SUCCESS_MESSAGE = "Email успешно подтверждён!"
    ERROR_MESSAGE = "Недействительная или просроченная ссылка."

    def get(self, request: Request, uidb64: str, token: str) -> Response:
        """
        Обрабатывает верификацию email.

        Args:
            uidb64: Base64-encoded user ID
            token: Verification token

        Returns:
            Response с результатом верификации
        """
        user = self._get_user_from_uidb64(uidb64)

        if user and self._is_token_valid(user, token):
            UserService.activate_user(user)
            return self._success_response()

        return self._error_response()

    @staticmethod
    def _get_user_from_uidb64(uidb64: str) -> User | None:
        """
        Извлекает пользователя из закодированного ID.

        Выделено в отдельный метод для:
        - Улучшения читаемости основного метода
        - Изоляции логики декодирования
        - Упрощения тестирования

        Returns:
            User или None при ошибке декодирования
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    @staticmethod
    def _is_token_valid(user: User, token: str) -> bool:
        return email_verification_token.check_token(user, token)

    def _success_response(self) -> Response:
        """Формирует успешный ответ."""
        return Response({"detail": self.SUCCESS_MESSAGE}, status=status.HTTP_200_OK)

    def _error_response(self) -> Response:
        """Формирует ответ с ошибкой."""
        return Response(
            {"detail": self.ERROR_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
        )


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    SUCCESS_MESSAGE = "Письмо с подтверждением отправлено на вашу почту."

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": self.SUCCESS_MESSAGE}, status=status.HTTP_201_CREATED
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("profile")
    permission_classes = [IsAdminUser]
    lookup_field = "nickname"

    def get_serializer_class(self):
        if self.action == "create":
            return RegisterSerializer
        return UserUpdateSerializer
