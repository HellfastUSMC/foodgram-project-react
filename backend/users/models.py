from django.db import models
from django.contrib.auth import get_user_model

from food.models import Ingridient

user = get_user_model()

# Create your models here.
class Subscribition(models.Model):
    author = models.ForeignKey(user, related_name='subscribitions', on_delete=models.CASCADE)
    subscriber = models.ForeignKey(user, related_name='subscribers', on_delete=models.CASCADE)


class ShoppingCart(models.Model):
    customer = models.ForeignKey(
        user,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Список покупок'
    )
    recipes = models.ManyToManyField(Ingridient, related_name='shopping_carts', blank=True, null=True)
