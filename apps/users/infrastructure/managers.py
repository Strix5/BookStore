from django.contrib.auth.base_user import BaseUserManager


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
