import glob
import json
import os
from datetime import date, datetime

from .api import SpoonacularAPI
from ..unit_utils import time_str_to_second


def append_diet(dest, diet):
    if 'suitableForDiet' not in dest:
        dest['suitableForDiet'] = []
    dest['suitableForDiet'].append(diet)


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

    def fetch_one(self):
        spoonacular = SpoonacularAPI(self.__api_key)
        print('start to get random recipe')
        source = spoonacular.random_recipe()
        now_str = datetime.now().strftime('%Y%m%d-%H%M%S.%f')
        raw_filename = os.path.join(self.__storage, f'raw_{now_str}.json')
        print(f'write raw to {raw_filename}')
        with open(raw_filename, 'w') as raw_fp:
            json.dump(source, raw_fp, indent=4, sort_keys=True)
        print('convert to our format')
        recipe = self.convert_recipe(source)
        self.save_recipe(recipe)

    def save_recipe(self, recipe):
        data_year = date.today().year
        data_week = date.today().isocalendar().week
        filename = os.path.join(self.__storage, f'recipes_{data_year}_{data_week}.json')
        if os.path.isfile(filename):
            print(f'append recipe to {filename}')
            with open(filename, 'r') as fp:
                output = json.load(fp)
        else:
            print(f'write recipe to {filename}')
            output = []
        output.append(recipe)
        with open(filename, 'w') as fp:
            json.dump(output, fp)
        print('done')

    def delete_output(self):
        print('remove all output recipes')
        recipe_files = glob.glob(os.path.join(self.__storage, 'recipes_*.json'), recursive=True)
        for recipe_file in recipe_files:
            os.remove(recipe_file)

    def reconvert(self):
        self.delete_output()
        raw_files = glob.glob(os.path.join(self.__storage, 'raw_*.json'), recursive=True)
        for raw_file in raw_files:
            print(f'reconvert file: {raw_file}')
            with open(raw_file, 'r') as fp:
                source = json.load(fp)
            recipe = self.convert_recipe(source)
            self.save_recipe(recipe)
