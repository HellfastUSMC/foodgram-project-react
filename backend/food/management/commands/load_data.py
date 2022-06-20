from csv import DictReader
from django.core.management import BaseCommand

from food.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):

        if Product.objects.exists():
            print('Данные уже присутствуют, выход...')
            return

        print('Начинаем загрузку данных')

        for row in DictReader(open('./data/ingredients.csv')):
            product = Product(name=row[0], measurement_unit=row[1])
            product.save()
