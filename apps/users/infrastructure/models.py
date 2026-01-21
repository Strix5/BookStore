from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        *,
        nickname: str,
        email: str,
        password: str,
        age: int,
        **extra_fields
    ):
        if not all((nickname, email, password, age)):
            raise ValueError("Nickname, Email, Password and Age are required.")

        if age < 0:
            raise ValueError("Age must be positive.")

        user = self.model(
            nickname=nickname.strip(),
            email=self.normalize_email(email),
            age=age,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            *,
            nickname: str,
            email: str,
            password: str,
            age: int = 18,
            **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not all((extra_fields.get("is_staff"), extra_fields.get("is_superuser"))):
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")

        return self.create_user(
            nickname=nickname,
            email=email,
            password=password,
            age=age,
            **extra_fields,
        )


class Profile(models.Model):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="profile",
        blank=True,
        null=True,
    )
    biography = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="profile/%y/%m/%d/", max_length=255, blank=True, null=True
    )

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")


class CustomUser(PermissionsMixin, AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=255, unique=True, db_index=True)
    age = models.PositiveSmallIntegerField(default=0)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    REQUIRED_FIELDS = ["nickname", "first_name", "last_name", "age"]
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ("email",)

    def __str__(self):
        return self.nickname

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
