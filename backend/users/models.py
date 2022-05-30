from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()

# Create your models here.
class Subscribition(models.Model):
    author = models.ManyToManyField(user, related_name='subscribitions')
    subscriber = models.ManyToManyField(user, related_name='subscribers')