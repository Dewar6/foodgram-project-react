import csv
import os

# from django.conf import settings
from recipes.models import Ingredient, MeasurementUnit

# file_path = os.path.join(settings.BASE_DIR, 'media', 'ingredients.csv')

# def load_ingredients_from_csv(file_path):
with open('ingredients.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=",")
    for row in reader:
        name = row[0]  
        unit_name = row[1]  
        unit, created = MeasurementUnit.objects.get_or_create(name=unit_name)
        ingredient = Ingredient(name=name, measurement_unit=unit)
        ingredient.save()
        # print(name, unit_name)
