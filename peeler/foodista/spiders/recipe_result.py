import logging
from datetime import datetime, timezone
from typing import List, Optional

from scrapy import Request, Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeItem
from ...utils.storage import Storage


logger = logging.getLogger(__name__)
DIET_TAG_MAP = {
    'gluten-free': 'GlutenFreeDiet',
    'vegetarian': 'VegetarianDiet'
}


def reformat_datetime(value: str):
    # since we don't know the timezone settings of Foodista, we just assume the datetime is UTC.
    return datetime.strptime(value, '%A, %B %d, %Y - %I:%M%p').replace(tzinfo=timezone.utc).isoformat()


def parse_yield(response: Response) -> Optional[dict]:
    yield_number = response.css('[itemprop=recipeYield]::text').get()
    if not yield_number:
        return None
    try:
        return {'number': int(yield_number), 'unit': 'people'}
    except ValueError:
        return None


def parse_suitable_for_diet(response: Response) -> Optional[List[str]]:
    tags = response.css('.field-name-field-tags .field-item a::text').getall()
    tags = [tag.lower() for tag in tags]
    result = []
    for (tag, diet) in DIET_TAG_MAP.items():
        if tag in tags:
            result.append(diet)
    return result if result else None


class RecipeResultSpider(Spider):
    name = 'recipe_result'
    allowed_domains = ['foodista.com']

    def start_requests(self):
        storage = Storage(self.settings['storage'])
        urls = storage.lock_recipe_urls(self.settings['peel_count'])
        for url in urls:
            yield Request(url=url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        logger.error(repr(failure))
        storage = Storage(self.settings['storage'])
        storage.unlock_recipe_url(failure.request.url)

    def parse(self, response: Response, **kwargs):
        storage = Storage(self.settings['storage'])
        try:
            item = RecipeItem(
                authors=[response.css('.username::text').get().strip()],
                categories=response.css('.field-name-field-tags .field-item a::text').getall(),
                dateCreated=reformat_datetime(response.css('.pane-node-created .pane-content::text').get().strip()),
                description='\n'.join(response.css('.field-name-body p::text').getall()),
                id=response.url,
                images=[response.css('[itemprop=image]').attrib['src']],
                ingredientsRaw=response.css('[itemprop=ingredients]::text').getall(),
                instructionsRaw=response.css('[itemprop=recipeInstructions]::text').getall(),
                keywords=response.css('.field-name-field-tags .field-item a::text').getall(),
                language=response.css('html').attrib['xml:lang'],
                mainLink=response.url,
                title=response.css('[itemprop=name]::text').get().strip(),
                yield_data=parse_yield(response),
                suitableForDiet=parse_suitable_for_diet(response)
            )
            logger.info(f'{response.url} is parsed successfully')
            storage.mark_finished(response.url)
            yield item
        except Exception as ex:
            logger.error(f'translate url, {response.url}, error: {repr(ex)}')
            storage.unlock_recipe_url(response.url)
            raise ex
