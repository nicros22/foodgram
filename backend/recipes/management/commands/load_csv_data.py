import csv
import logging
import os

from pathlib import Path
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

DATA_NAMES = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        for model, csv_filename in DATA_NAMES.items():
            with open(Path(__file__).parents[5] / 'data' / csv_filename, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                data_to_insert = [
                    model(
                        name=row[0],
                        measurement_unit=row[1]
                    ) for row in reader
                ]
                model.objects.bulk_create(data_to_insert)
                logger.info('Данные из csv-файла были успешно загружены')