from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.users.infrastructure.tokens import email_verification_token


User = get_user_model()


@shared_task
def send_verification_email_task(user_id: int, *, domain: str, scheme: str = "http"):
    """
    Отправляет письмо верификации email асинхронно.
    domain: например "192.168.1.1:8000" или "api.example.com"
    scheme: "http" или "https"
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    path = reverse("users:verify-email", kwargs={"uidb64": uidb64, "token": token})
    verify_link = f"{scheme}://{domain}{path}"

    send_mail(
        subject="Подтверждение регистрации",
        message=f"Привет, {user.nickname}!\nПерейди по ссылке, чтобы подтвердить аккаунт:\n{verify_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    return user
