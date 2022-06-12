from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
# from django.contrib.auth.hashers import make_password
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True, max_length=254)
    username = models.CharField('username', unique=True, max_length=150, validators=[RegexValidator(r'^[\w.@+-]+\Z', 'Имя пользователя содержит недопустимые символы')])
    first_name = models.CharField('first name', max_length=150)
    last_name = models.CharField('last name', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomUserManager()

    # def set_password(self, raw_password):
    #     self.password = make_password(raw_password)
    #     self._password = raw_password

    def __str__(self):
        return self.email
