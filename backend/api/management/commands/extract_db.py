import csv
import os
import traceback

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

ERROR_MESSAGE = """
Если в БД существуют данные, требуется удалить бд и заново провести
миграции для создания пустой бд.
"""


class Command(BaseCommand):

    def handle(self, *args, **options,):
        if Ingredient.objects.exists():
            print(ERROR_MESSAGE)
            return

        try:
            self.load_data_from_csv(
                'ingredients.csv',
                Ingredient,
                name='ингредиент',
                measurement_unit='мера'
            )
            print('Импорт завершён')
        except Exception:
            traceback.print_exc()

    def load_data_from_csv(self, filename, model_class, **field_names):
        try:
            with open(
                os.path.join(settings.BASE_DIR, 'data', filename),
                encoding='utf-8'
            ) as file:
                for row in csv.DictReader(file):
                    kwargs = {}
                    for field_name, csv_column_name in field_names.items():
                        kwargs[field_name] = row[csv_column_name]
                    model_instance = model_class(**kwargs)
                    model_instance.save()
        except ValueError:
            print('Значение неопределенно')
        except Exception:
            raise
