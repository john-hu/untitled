import glob
import json
import os
from datetime import date, datetime

from .api import SpoonacularAPI
from ..utils.files import append_to
from ..utils.units import time_str_to_second

RAW_PREFIX = 'raw'
RECIPE_PREFIX = 'recipes'
USED_MAX_QUOTA = 120


def append_diet(dest, diet):
    if 'suitableForDiet' not in dest:
        dest['suitableForDiet'] = []
    dest['suitableForDiet'].append(diet)


class OverQuotaError(Exception):
    def __init__(self, message, quota):
        super().__init__(message if message else 'Over quota')
        self.quota = quota


class SpoonacularPeeler:
    DIET_MAP = {
        'vegetarian': 'VegetarianDiet',
        'vegan': 'VeganDiet',
        'lowFodmap': 'LowFodmapDiet',
        'glutenFree': 'GlutenFreeDiet'
    }

    def __init__(self, api_key, storage):
        self.__api_key = api_key
        self.__storage = storage
        os.makedirs(storage, exist_ok=True)

    def convert_diet(self, source, dest):
        for (source_key, dest_value) in enumerate(self.DIET_MAP):
            if source.get(source_key, False):
                append_diet(dest, dest_value)

    @staticmethod
    def convert_ingredient(source, dest):
        ingredients = source.get('extendedIngredients', [])
        dest['ingredients'] = []
        for ingredient in ingredients:
            dest['ingredients'].append({
                'name': ingredient.get('nameClean', ingredient.get('name', ingredient.get('originalName', ''))),
                'size': {
                    'number': ingredient.get('amount', 0),
                    'unit': ingredient.get('unit', '')
                }
            })

    @staticmethod
    def convert_instructions(source, dest):
        assert 'analyzedInstructions' in source and source['analyzedInstructions']
        instructions = source.get('analyzedInstructions')[0].get('steps', [])
        dest['instructions'] = []
        dest['equipments'] = []
        for instruction in instructions:
            dest_instruction = {
                'id': str(instruction.get('number')),
                'equipments': [equipment.get('name', '') for equipment in instruction.get('equipment')],
                'language': 'en',
                'text': instruction.get('step'),
            }
            # copy equipments and dedupe
            dest['equipments'] = dest['equipments'] + list(
                set(dest_instruction['equipments']) - set(dest['equipments']))
            if 'length' in instruction:
                time_required = instruction.get('length')
                dest_instruction['timeRequired'] = time_required.get('number') * time_str_to_second(
                    time_required.get('unit'))
            dest['instructions'].append(dest_instruction)

    def convert_recipe(self, source):
        dest = {
            'authors': ['anonymous'],
            'categories': source['dishTypes'] if source.get('dishTypes', None) else ['uncategorized'],
            'cookTime': source.get('readyInMinutes', 0) * 60, 'description': source.get('summary', ''),
            'language': 'en'
        }
        assert 'title' in source
        dest['keywords'] = [source.get('title')]
        if source.get('cuisines', None):
            dest['cuisines'] = source.get('cuisines')
        assert 'sourceUrl' in source
        dest['id'] = source.get('sourceUrl')
        dest['mainLink'] = source.get('sourceUrl')
        if source.get('image', None):
            dest['images'] = [source.get('image')]
        assert 'sourceName' in source
        dest['sourceSite'] = source.get('sourceName')
        assert 'title' in source
        dest['title'] = source.get('title')
        if 'servings' in source:
            dest['servingSize'] = {
                'number': source.get('servings'),
                'unit': 'people'
            }
        self.convert_diet(source, dest)
        self.convert_ingredient(source, dest)
        self.convert_instructions(source, dest)
        return dest

    def is_out_of_quote(self):
        quota_file = os.path.join(self.__storage, 'quota.json')
        if os.path.isfile(quota_file):
            with open(quota_file, 'r') as fp:
                quota = json.load(fp)
        else:
            quota = {
                'utc': datetime.utcnow().strftime('%Y%m%d'),
                'used': 0
            }
        today_utc = datetime.utcnow().strftime('%Y%m%d')
        quota_utc = quota['utc']
        if today_utc != quota_utc:
            print(f'switch date from {quota_utc} to {today_utc} (utc) reset used')
            quota['utc'] = today_utc
            quota['used'] = 0
        return quota['used'] > USED_MAX_QUOTA, quota['used']

    def update_quote(self, quota):
        quota_file = os.path.join(self.__storage, 'quota.json')
        quota_data = {
            'utc': datetime.utcnow().strftime('%Y%m%d'),
            'used': quota
        }
        with open(quota_file, 'w') as fp:
            json.dump(quota_data, fp)

    def fetch_one(self):
        over_quota, used = self.is_out_of_quote()
        if over_quota:
            raise OverQuotaError(f'out of quote: {used}', used)
        spoonacular = SpoonacularAPI(self.__api_key)
        print('start to get random recipe')
        source = spoonacular.random_recipe()
        self.update_quote(spoonacular.used_quote)
        try:
            recipe = self.convert_recipe(source)
            self.save_recipe(recipe, False)
            # Optional: save source recipe for further investigation
            self.save_recipe(source, True)
        except AssertionError:
            print('error found, unable to save')
            today_str = date.today().strftime('%Y%m%d')
            append_to(self.__storage, 'error', today_str, source)

    def save_recipe(self, recipe, raw=False, today_str=None):
        prefix = RAW_PREFIX if raw else RECIPE_PREFIX
        if not today_str:
            today_str = date.today().strftime('%Y%m%d')
        append_to(self.__storage, prefix, today_str, recipe)

    def delete_output(self):
        print('remove all output recipes')
        recipe_files = glob.glob(os.path.join(self.__storage, f'{RECIPE_PREFIX}_*.json'), recursive=True)
        for recipe_file in recipe_files:
            os.remove(recipe_file)

    def reconvert(self):
        self.delete_output()
        raw_files = glob.glob(os.path.join(self.__storage, f'{RAW_PREFIX}_*.json'), recursive=True)
        for raw_file in raw_files:
            print(f'reconvert file: {raw_file}')
            # load the file
            with open(raw_file, 'r') as fp:
                sources = json.load(fp)
            # parse the date string from file, + 1 for '_', -5 for '.json'
            basename = os.path.basename(os.path.normpath(raw_file))
            date_str = basename[len(RAW_PREFIX) + 1:-5]

            # since we have 100 quota per day, it won't break 500 limitations.
            for source in sources:
                self.save_recipe(self.convert_recipe(source), today_str=date_str)
