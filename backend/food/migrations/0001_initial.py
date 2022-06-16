# Generated by Django 2.2.16 on 2022-06-16 14:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название продукта')),
                ('measurement_unit', models.CharField(max_length=30, verbose_name='Единицы измерения')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('published', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('image', models.ImageField(max_length=5500000, upload_to='recipes/images', verbose_name='Обложка')),
                ('text', models.TextField(max_length=1000, verbose_name='Описание')),
                ('cooking_time', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5000)], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-published'],
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='Название')),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.MinLengthValidator(7), django.core.validators.MaxLengthValidator(7)], verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=30, unique=True, verbose_name='Slug')),
            ],
        ),
    ]