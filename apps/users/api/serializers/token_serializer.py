from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор для получения JWT токенов.

    Расширяет стандартный SimpleJWT сериализатор:
    - Добавляет проверку активации email
    - Включает данные пользователя в ответ
    """

    # Константа для улучшения читаемости и возможности изменения
    ERROR_CODE_INACTIVE = "user_inactive"
    ERROR_MESSAGE_INACTIVE = "Email not verified"

    def validate(self, attrs):
        """
        Валидация и генерация токенов.

        Проверяет:
        1. Правильность учетных данных (делает родительский класс)
        2. Активацию пользователя (is_active)
        3. Добавляет данные пользователя в ответ
        """
        data = super().validate(attrs)
        user = self.user

        # Проверка активации email
        if not user.is_active:
            raise AuthenticationFailed(
                detail=self.ERROR_MESSAGE_INACTIVE, code=self.ERROR_CODE_INACTIVE
            )

        # Добавляем данные пользователя в ответ
        data["user"] = self._get_user_data(user)

        return data

    @staticmethod
    def _get_user_data(user: User) -> dict:
        """
        Формирует данные пользователя для ответа.

        Выделено в отдельный метод для:
        - Единообразного формирования ответа
        - Возможности переопределения в подклассах
        - Упрощения тестирования
        """
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
        }
