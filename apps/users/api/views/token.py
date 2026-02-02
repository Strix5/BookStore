from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.api.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Получение JWT токенов с дополнительной валидацией.

    Использует кастомный сериализатор для:
    - Проверки активации email
    - Добавления данных пользователя в ответ
    """

    serializer_class = CustomTokenObtainPairSerializer
