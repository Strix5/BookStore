from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.api.routers import router
from apps.users.api.views import CustomTokenObtainPairView, RegisterView, VerifyEmailView

app_name = "users"


urlpatterns = [
    path(
        "verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify-email"
    ),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
