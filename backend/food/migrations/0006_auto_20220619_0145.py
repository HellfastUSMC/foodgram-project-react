# Generated by Django 2.2.16 on 2022-06-18 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0005_auto_20220619_0122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/images', verbose_name='Обложка'),
        ),
    ]
