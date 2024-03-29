from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(
        self, username, email, first_name,
        last_name, password, **extra_fields
    ):
        if not email:
            raise ValueError('Поле email - обязательное')
        if not username:
            raise ValueError('Поле псевдоним - обязательное')
        if not first_name:
            raise ValueError('Поле имя - обязательное')
        if not last_name:
            raise ValueError('Поле фамилия - обязательное')
        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, first_name=first_name,
            last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, email, first_name, last_name, password, **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(
            username, email, first_name, last_name, password, **extra_fields
        )
