from enum import unique
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    MinLengthValidator,
                                    MaxLengthValidator
                                    )


user = get_user_model()


class Unit(models.Model):
    name = models.CharField('Единица измерения', max_length=30, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название продукта', max_length=30, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название', max_length=30, unique=True)
    color = models.CharField(
        'Цвет',
        max_length=7, 
        validators=[MinLengthValidator(7), MaxLengthValidator(7)],
        unique=True
    )
    slug = models.SlugField('Slug', unique=True)

    def __str__(self):
        return self.name


class Ingridient(models.Model):
    name = models.ManyToManyField(
        Product,
        verbose_name='Название продукта',
        related_name='ingridient'
    )
    volume = models.FloatField(
        'Количество',
        validators=[MinValueValidator(0.0)]
    )
    units = models.ManyToManyField(
        Unit,
        verbose_name='Единицы измерения',
        related_name='ingridient'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        user, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Обложка')
    text = models.TextField('Описание')
    ingridients = models.ManyToManyField(Ingridient, related_name='recipes')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[MinValueValidator(1)]
    )
    favorites = models.ManyToManyField(user, related_name='favorites')

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    customer = models.ForeignKey(
        user, on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Список покупок'
    )
    goods = models.ManyToManyField(Ingridient, related_name='shopping_carts')
