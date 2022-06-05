from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()

# Create your models here.
class Subscribition(models.Model):
    author = models.ForeignKey(user, related_name='subscribitions', on_delete=models.CASCADE, default='1')
    subscriber = models.ForeignKey(user, related_name='subscribers', on_delete=models.CASCADE, default='1')