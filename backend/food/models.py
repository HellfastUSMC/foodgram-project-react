from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    MinLengthValidator,
                                    MaxLengthValidator
                                    )


user = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=30, unique=True)
    color = models.CharField(
        'Цвет',
        max_length=7, 
        validators=[MinLengthValidator(7), MaxLengthValidator(7)],
        unique=True
    )
    slug = models.SlugField('Slug', unique=True)


class Ingridient(models.Model):
    pass


class Recipe(models.Model):
    author = models.ForeignKey(
        user, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=128)
    image = models.ImageField('Обложка')
    info = models.TextField('Описание')
    ingridients = models.ManyToManyField(Ingridient, related_name='recipes')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cook_time = models.TimeField(
        'Время приготовления',
        validators=[MinValueValidator(0)]
    )
