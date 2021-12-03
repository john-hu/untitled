import logging

from scrapy.http import Response

from ...scrapy_utils.spiders.base import BaseResultSpider, InvalidResponseData
from ...scrapy_utils.items import RecipeItem
from ...utils.parsers import as_array, parse_duration, parse_yield, split, tags_to_diet
from ...utils.schema_org import find_json_by_schema_org_type, parse_authors, parse_nutrition_info, \
    parse_suitable_for_diet, parse_video_urls

logger = logging.getLogger(__name__)
DIET_TAG_MAP = {
    'tasty_vegetarian': 'VegetarianDiet'
}


# Tasty support schema.org Recipe format at
# `head script[type="application/ld+json"]` ;).
class RecipeResultSpider(BaseResultSpider):
    allowed_domains = ['tasty.co']
    json_css_path = 'head script[type="application/ld+json"]::text'

    def parse_response(self, response: Response) -> RecipeItem:
        if len(response.css(self.json_css_path)) == 0:
            raise InvalidResponseData(field='json')
        recipe = find_json_by_schema_org_type(
            response.css(self.json_css_path).getall(), 'Recipe')
        InvalidResponseData.check_and_raise(recipe, 'name')
        InvalidResponseData.check_and_raise(recipe, 'recipeIngredient')
        InvalidResponseData.check_and_raise(recipe, 'recipeInstructions')

        recipe_language = BaseResultSpider.parse_html_language(response)

        item = RecipeItem(
            categories=recipe.get('recipeCategory', None),
            id=response.request.url,
            keywords=split(recipe.get('keywords', None)),
            language=recipe_language,
            sourceSite='Tasty',
            title=recipe['name'],
            mainLink=response.url,
            version='raw'
        )
        item.authors = parse_authors(recipe.get('author', 'Tasty'))
        item.categories = as_array(recipe.get('recipeCategory', None))
        item.cookingMethods = as_array(recipe.get('cookingMethod', None))
        item.cookTime = parse_duration(recipe.get('cookTime'))
        item.cuisines = as_array(recipe.get('recipeCuisine', None))
        item.dateCreated = recipe.get('datePublished', None)
        item.dateModified = recipe.get('uploadDate', None)
        item.description = recipe.get('description', None)
        item.images = as_array(recipe.get('image', None))
        item.ingredientsRaw = recipe.get('recipeIngredient', None)
        item.instructionsRaw = [
            instruction['text'] for instruction in recipe.get(
                'recipeInstructions', [])]
        item.nutrition = parse_nutrition_info(recipe.get('nutrition', None))
        item.videos = parse_video_urls(recipe.get('video', None))
        item.suitableForDiet = parse_suitable_for_diet(
            recipe.get('suitableForDiet', None))
        if not item.suitableForDiet:
            item.suitableForDiet = tags_to_diet(item.keywords, DIET_TAG_MAP)
        if recipe.get('recipeYield', None):
            item.yield_data = parse_yield(recipe['recipeYield'])
        # Some data containing nutrition. It's hard to parse it now. Just skip
        # it at this version.
        RecipeItem.fill_recipe_presets(item)
        return item
