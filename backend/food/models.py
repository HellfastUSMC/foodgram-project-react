from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxLengthValidator, MaxValueValidator, MinLengthValidator,
    MinValueValidator,
)
from django.db import models

user = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=30, unique=True)
    color = models.CharField(
        'Цвет',
        max_length=7,
        validators=[MinLengthValidator(7), MaxLengthValidator(7)],
        unique=True
    )
    slug = models.SlugField('Slug', unique=True, max_length=30)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name} {self.color}'


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

    class Meta:
        ordering = ['name']
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        user, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    published = models.DateTimeField('Дата публикации', auto_now_add=True)
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Обложка',
        upload_to='recipes/images'
    )
    text = models.TextField('Описание', max_length=1000)
    ingredients = models.ManyToManyField(
        Product,
        through='Ingredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} {self.author.username}'


class Ingredient(models.Model):

    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['product', 'recipe'],
                                    name='unique_product_recipe')
        ]

    def __str__(self):
        return (f'{self.product.name} {self.amount}'
                f'{self.product.measurement_unit}')


class Subscription(models.Model):
    author = models.ForeignKey(
        user, related_name='subscriptions',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    subscriber = models.ForeignKey(
        user,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['author', 'subscriber'],
                                    name='unique_author_subscriber')
        ]

    def __str__(self):
        return (f'Подписка - автор: {self.author.email}'
                f', подписчик: {self.subscriber.email}')


class ShoppingCart(models.Model):
    customer = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Покупатель'
    )
    recipes = models.ManyToManyField(
        Recipe,
        related_name='shopping_carts',
        blank=True,
        verbose_name='Рецепты'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['customer', ],
                                    name='unique_customer')
        ]

    def __str__(self):
        return f'Корзина {self.customer.username}'
