import csv

from django.core.management import BaseCommand

from food.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):

        print('Начинаем загрузку данных')

        with open('./data/ingredients.csv') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row[0])
                _, created = Product.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
