from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.infrastructure.managers import CustomUserManager


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
        upload_to="profile/%y/%m/%d/",
        max_length=255,
        blank=True,
        null=True
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
