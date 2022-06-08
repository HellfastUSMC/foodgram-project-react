from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    MinLengthValidator,
                                    MaxLengthValidator
                                    )


user = get_user_model()


# class Unit(models.Model):
#     name = models.CharField('Единица измерения', max_length=30, unique=True)

#     def __str__(self):
#         return self.name


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


class Product(models.Model):
    name = models.CharField(
        verbose_name='Название продукта',
        max_length=200,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=30
    )

    def __str__(self):
        return self.name


class Ingridient(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='ingridients',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.product.name


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
        validators=[MinValueValidator(1), MaxValueValidator(5000)]
    )
    favorites = models.ManyToManyField(
        user,
        verbose_name='Избранное',
        related_name='favorites',
        blank=True,
    )

    def __str__(self):
        return self.name


class Subscription(models.Model):
    author = models.ForeignKey(user, related_name='subscriptions', on_delete=models.CASCADE)
    subscriber = models.ForeignKey(user, related_name='subscribers', on_delete=models.CASCADE)

    def __str__(self):
        return f'Подписка - автор: {self.author.email}, подписчик: {self.subscriber.email}'


class ShoppingCart(models.Model):
    customer = models.ForeignKey(
        user,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Покупатель'
    )
    recipes = models.ManyToManyField(Recipe, related_name='shopping_carts', blank=True)

    def __str__(self):
        return f'Корзина {self.customer.username}'