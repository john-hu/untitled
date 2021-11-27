import json
import jsonschema
import logging
import os
from argparse import ArgumentParser

logger = logging.getLogger(__name__)

recipe_schema_file = os.path.join('doc', 'recipe_json_schema', 'Recipe.json')
if os.path.exists(recipe_schema_file):
    with open(recipe_schema_file, 'r') as fp:
        recipe_schema = json.load(fp)
else:
    recipe_schema = None


def validate(recipe: dict):
    try:
        jsonschema.validate(recipe, recipe_schema)
        # TODO: we found an issue at our recipe schema, check #71. workaround it
        if not recipe.get('instructions', None) and not recipe.get('instructionsRaw', None):
            raise Exception('instructions and instructionsRaw are all none')
        if not recipe.get('ingredients', None) and not recipe.get('ingredientsRaw', None):
            raise Exception('instructions and instructionsRaw are all none')
    except jsonschema.ValidationError as ex:
        logger.error(json.dumps(recipe, indent=4))
        logger.error(f'validation error at {ex.path} / {ex.json_path} of {ex.schema_path}')
        raise ex


def run():
    parser = ArgumentParser(f'peeler data to silver plate uploader')
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    with open(args.file, 'r') as file:
        data = json.load(file)
        for recipe in data:
            validate(recipe)


if __name__ == '__main__':
    run()
