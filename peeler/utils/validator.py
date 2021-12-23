import json
import logging
import os
from argparse import ArgumentParser

import jsonschema

logger = logging.getLogger(__name__)

recipe_schema_file = os.path.join('doc', 'recipe_json_schema', 'Recipe.json')
if os.path.exists(recipe_schema_file):
    with open(recipe_schema_file, 'r', encoding="UTF-8") as fp:
        recipe_schema = json.load(fp)
else:
    recipe_schema = None


def validate(recipe: dict):
    try:
        jsonschema.validate(recipe, recipe_schema)
    except jsonschema.ValidationError as ex:
        logger.error(json.dumps(recipe, indent=4))
        logger.error(f'validation error at {ex.path} / {ex.json_path} of {ex.schema_path}')
        raise ex


def run():
    parser = ArgumentParser('peeler data to silver plate uploader')
    parser.add_argument('file', type=str)
    args = parser.parse_args()
    with open(args.file, 'r', encoding="UTF-8") as file:
        data = json.load(file)
        for recipe in data:
            validate(recipe)


if __name__ == '__main__':
    run()
