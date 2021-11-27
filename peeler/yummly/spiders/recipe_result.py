import logging
from typing import List

from scrapy.http import Response

from ...scrapy_utils.spiders.base import BaseResultSpider, InvalidResponseData
from ...scrapy_utils.items import RecipeItem
from ...utils.schema_org import find_json_by_schema_org_type

logger = logging.getLogger(__name__)


# Yummly support schema.org Recipe format at
# `#mainApp .App .app-content .recipe .structured-data-info script[type="application/ld+json"]` ;).
class RecipeResultSpider(BaseResultSpider):
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

    def parse_response(self, response: Response) -> RecipeItem:
        if len(response.css(self.json_css_path)) == 0:
            raise InvalidResponseData(field='json')
        recipe = find_json_by_schema_org_type(response.css(self.json_css_path).getall(), 'Recipe')
        InvalidResponseData.check_and_raise(recipe, 'name')
        InvalidResponseData.check_and_raise(recipe, 'recipeIngredient')
        InvalidResponseData.check_and_raise(recipe, 'recipeInstructions')
        recipe_language = BaseResultSpider.parse_html_language(response)

        item = RecipeItem.from_schema_org(recipe)
        if not item:
            raise InvalidResponseData(field='json schema')
        item.language = recipe_language
        item.sourceSite = 'Yummly'
        if not recipe.get('url', None):
            item.id = response.request.url
            item.mainLink = response.request.url
        item.ingredients = self.parse_ingredient(response)
        item.instructions = self.parse_instructions(recipe, recipe_language)
        item.version = 'parsed'
        return item
