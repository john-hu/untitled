import json
import logging
from typing import List

from scrapy.http import Response

from ...scrapy_utils.base_spiders import BaseResultSpider, InvalidResponseData
from ...scrapy_utils.items import RecipeItem
from ...utils.parsers import as_array, isodate_2_isodatetime, parse_duration, parse_yield, split
from ...utils.schema_org import parse_authors, parse_nutrition_info, parse_suitable_for_diet

logger = logging.getLogger(__name__)


# Yummly support schema.org Recipe format at
# `#mainApp .App .app-content .recipe .structured-data-info script[type="application/ld+json"]` ;).
class RecipeResultSpider(BaseResultSpider):
    allowed_domains = ['yummly.co.uk']
    json_css_path = '.recipe .structured-data-info script[type="application/ld+json"]::text'

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
        # It has two structured-data-info. We should get the first one.
        recipe = json.loads(response.css(self.json_css_path)[0].get())
        InvalidResponseData.check_and_raise(recipe, 'name')
        InvalidResponseData.check_and_raise(recipe, 'recipeIngredient')
        InvalidResponseData.check_and_raise(recipe, 'recipeInstructions')
        recipe_language = BaseResultSpider.parse_html_language(response)
        item = RecipeItem(
            authors=parse_authors(recipe.get('author', 'Yummly')),
            categories=as_array(recipe.get('recipeCategory', None)),
            id=response.request.url,
            keywords=split(recipe.get('keywords', None)),
            language=recipe_language,
            sourceSite='Yummly',
            title=recipe['name'],
            mainLink=response.url,
            version='parsed'
        )
        item.cookingMethods = as_array(recipe.get('cookingMethod', None))
        item.cookTime = parse_duration(recipe.get('cookTime'))
        item.cuisines = as_array(recipe.get('recipeCuisine', None))
        item.dateCreated = isodate_2_isodatetime(recipe.get('dateCreated', None))
        item.dateModified = isodate_2_isodatetime(recipe.get('dateModified', None))
        item.description = recipe.get('description', None)
        item.images = as_array(recipe.get('image', None))
        item.ingredients = self.parse_ingredient(response)
        item.instructions = self.parse_instructions(recipe, recipe_language)
        item.nutrition = parse_nutrition_info(recipe.get('nutrition', None))
        item.suitableForDiet = parse_suitable_for_diet(recipe.get('suitableForDiet', None))
        if recipe.get('recipeYield', None):
            item.yield_data = parse_yield(recipe['recipeYield'])
        # Some data containing nutrition. It's hard to parse it now. Just skip it at this version.
        BaseResultSpider.fill_recipe_presets(item)
        return item