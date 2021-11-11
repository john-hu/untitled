import logging

from scrapy.http import Response

from ...scrapy_utils.base_spiders import BaseResultSpider, InvalidResponseData
from ...scrapy_utils.items import RecipeItem
from ...utils.parsers import get_attribute, parse_duration, parse_yield, tags_to_diet

logger = logging.getLogger(__name__)
DIET_TAG_MAP = {
    'vegetarian': 'VegetarianDiet'
}


class RecipeResultSpider(BaseResultSpider):
    allowed_domains = ['foodnetwork.co.uk']

    def parse_response(self, response: Response) -> RecipeItem:
        if not response.css('[itemprop=recipeIngredient]') or not response.css('[itemprop=recipeInstructions]'):
            raise InvalidResponseData()
        item = RecipeItem(
            authors=[get_attribute(response.css('.recipe-page meta[itemprop=author]'), 'content', 'Food Network')],
            dateCreated=get_attribute(response.css('meta[itemprop=datePublished]'), 'content'),
            description=get_attribute(response.css('meta[name=description]'), 'content'),
            id=response.request.url,
            ingredientsRaw=response.css('[itemprop=recipeIngredient]::text').getall(),
            instructionsRaw=response.css('[itemprop=recipeInstructions] p::text').getall(),
            language=response.css('meta[property="og:locale"]').attrib['content'].strip(),
            mainLink=response.url,
            sourceSite='Food Network',
            title=response.css('[itemprop=name]::text').get().strip()
        )
        if response.css('meta[itemprop=image]'):
            item.images = [response.css('meta[itemprop=image]').attrib['content'].strip()]
        if response.css('meta[itemprop=keywords]'):
            item.keywords = response.css('meta[itemprop=keywords]').attrib['content'].strip().split(', ')
            item.categories = item.keywords
        else:
            BaseResultSpider.fill_recipe_presets(item)
        if not item.instructionsRaw:
            # the second form of instructions @@.
            item.instructionsRaw = response.css('[itemprop=recipeInstructions] li::text').getall()
        if not item.instructionsRaw:
            # the third form of instructions @@.
            item.instructionsRaw = response.css('[itemprop=recipeInstructions]::text').getall()
        if response.css('meta[itemprop=cookTime]'):
            item.cookTime = parse_duration(response.css('meta[itemprop=cookTime]').attrib['content'].strip())
        if response.css('meta[itemprop=prepTime]'):
            item.prepTime = parse_duration(response.css('meta[itemprop=prepTime]').attrib['content'].strip())
        if response.css('meta[itemprop=recipeYield]'):
            item.yield_data = parse_yield(response.css('meta[itemprop=recipeYield]').attrib['content'].strip())
        item.suitableForDiet = tags_to_diet(item.keywords, DIET_TAG_MAP)
        return item
