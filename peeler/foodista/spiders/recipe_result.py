import logging
from datetime import datetime, timezone

from scrapy.http import Response

from ...scrapy_utils.spiders.base import BaseResultSpider
from ...scrapy_utils.items import RecipeItem
from ...utils.parsers import parse_yield, tags_to_diet

logger = logging.getLogger(__name__)
DIET_TAG_MAP = {
    'gluten-free': 'GlutenFreeDiet',
    'vegetarian': 'VegetarianDiet'
}


def reformat_datetime(value: str):
    # since we don't know the timezone settings of Foodista, we just assume
    # the datetime is UTC.
    return datetime.strptime(
        value, '%A, %B %d, %Y - %I:%M%p').replace(tzinfo=timezone.utc).isoformat()


class RecipeResultSpider(BaseResultSpider):
    allowed_domains = ['foodista.com']

    def parse_response(self, response: Response) -> RecipeItem:
        item = RecipeItem(
            authors=[response.css('.username::text').get().strip()],
            dateCreated=reformat_datetime(
                response.css('.pane-node-created .pane-content::text').get().strip()),
            description='\n'.join(
                response.css('.field-name-body p::text').getall()),
            id=response.request.url,
            images=[response.css('[itemprop=image]').attrib['src']],
            ingredientsRaw=response.css(
                '[itemprop=ingredients]::text').getall(),
            instructionsRaw=response.css(
                '[itemprop=recipeInstructions]::text').getall(),
            language=response.css('html').attrib['xml:lang'],
            mainLink=response.url,
            sourceSite='Foodista',
            title=response.css('[itemprop=name]::text').get().strip(),
            yield_data=parse_yield(
                response.css('[itemprop=recipeYield]::text').get())
        )
        if response.css('.field-name-field-tags .field-item a::text'):
            item.keywords = response.css(
                '.field-name-field-tags .field-item a::text').getall()
            item.categories = item.keywords
        else:
            RecipeItem.fill_recipe_presets(item)
        item.suitableForDiet = tags_to_diet(item.keywords, DIET_TAG_MAP)
        return item
