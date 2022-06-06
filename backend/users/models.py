from django.db import models
from django.contrib.auth import get_user_model

from food.models import Recipe

user = get_user_model()


class Subscribition(models.Model):
    author = models.ForeignKey(user, related_name='subscribitions', on_delete=models.CASCADE)
    subscriber = models.ForeignKey(user, related_name='subscribers', on_delete=models.CASCADE)


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
