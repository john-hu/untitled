import logging
from typing import Generator, List, Union

from scrapy.http import Response

from ...scrapy_utils.spiders.base import InvalidResponseData
from ...scrapy_utils.spiders.generator_base import GeneratorResultSpider
from ...scrapy_utils.items import RecipeItem, RecipeURLItem
from ...utils.schema_org import find_json_by_schema_org_type

logger = logging.getLogger(__name__)


class RecipeResultSpider(GeneratorResultSpider):
    allowed_domains = ['yummly.co.uk']
    json_css_path = '.structured-data-info script[type="application/ld+json"]::text'

    @staticmethod
    def parse_ingredient(response: Response) -> List[dict]:
        ingredients = []
        # ingredient data in recipe is text data. But we can find the structured data at the HTML.
        for ingredient in response.css('.IngredientLine'):
            ingredient_item = {
                'name': ingredient.css('.ingredient::text').get().strip(),
                'size': None
            }
            # if remainder has text, we should view it as the name (the same as the text in structured-data-info).
            if ingredient.css('.remainder::text'):
                ingredient_item['name'] += f' ({ingredient.css(".remainder::text").get().strip()})'
            if ingredient.css('.amount span::text'):
                number_text = ingredient.css('.amount span::text').get().strip().replace(',', '')
                ingredient_item['size'] = {'number': float(number_text)}
                # may we see an unit element without amount? I don't think so.
                if ingredient.css('.unit::text'):
                    ingredient_item['size']['unit'] = ingredient.css('.unit::text').get().strip()
                else:
                    ingredient_item['size']['unit'] = None
            if ingredient_item in ingredients:
                logger.warning(f'duplicated ingredient found {ingredient_item}')
            else:
                ingredients.append(ingredient_item)
        return ingredients

    @staticmethod
    def parse_instructions(recipe: dict, language: str) -> List[dict]:
        instructions = []
        for instruction in recipe.get('recipeInstructions', []):
            instruction_item = {
                'id': str(instruction['position']),
                'language': language,
                'text': instruction['text'],
                'authors': [instruction.get('author', 'Yummly')],
            }
            if instruction.get('image', None):
                instruction_item['images'] = [instruction['image']]
            instructions.append(instruction_item)
        return instructions

    @staticmethod
    def parse_raw_recipe(recipe: dict, language: str, url: str):
        item = RecipeItem.from_schema_org(recipe)
        if not item:
            raise InvalidResponseData(field='json schema')
        item.language = language
        item.sourceSite = 'Yummly'
        if not recipe.get('url', None):
            item.id = url
            item.mainLink = url
        return item

    def parse_recipe(self, recipe: dict, language: str, response: Response):
        InvalidResponseData.check_and_raise(recipe, 'name')
        InvalidResponseData.check_and_raise(recipe, 'recipeIngredient')
        InvalidResponseData.check_and_raise(recipe, 'recipeInstructions')

        item = self.parse_raw_recipe(recipe, language, response.request.url)
        item.ingredients = self.parse_ingredient(response)
        item.instructions = self.parse_instructions(recipe, language)
        item.version = 'parsed'
        return item

    def yield_results(self, response: Response) -> Generator[Union[RecipeItem, RecipeURLItem], None, None]:
        if len(response.css(self.json_css_path)) == 0:
            raise InvalidResponseData(field='json')
        recipe_language = RecipeResultSpider.parse_html_language(response)
        # if recipe found, yield it
        recipe = find_json_by_schema_org_type(response.css(self.json_css_path).getall(), 'Recipe')
        if recipe:
            yield self.parse_recipe(recipe, recipe_language, response)
        # if item list found, yield it
        item_list = find_json_by_schema_org_type(response.css(self.json_css_path).getall(), 'ItemList')
        if item_list:
            for recipe in item_list.get('itemListElement', []):
                # parse recipe type only
                if recipe.get('@type') == 'Recipe':
                    if recipe.get('url', None):
                        # We should put the url into database for detailed parser.
                        yield RecipeURLItem(url=recipe.get('url'))
                    yield self.parse_raw_recipe(recipe, recipe_language, response.request.url)
