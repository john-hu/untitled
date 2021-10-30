import logging

from scrapy import Request, Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeItem
from ...utils.parsers import get_attribute, parse_duration, parse_yield, tags_to_diet
from ...utils.storage import Storage

logger = logging.getLogger(__name__)
DIET_TAG_MAP = {
    'vegetarian': 'VegetarianDiet'
}


class RecipeResultSpider(Spider):
    name = 'recipe_result'
    allowed_domains = ['foodnetwork.co.uk']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__fetched_count = 0
        self.__total_count = 0

    def start_requests(self):
        storage = Storage(self.settings['storage'])
        urls = storage.lock_recipe_urls(self.settings['peel_count'])
        logger.info(f'locked urls count: {len(urls)}')
        self.__total_count = len(urls)
        for url in urls:
            yield Request(url=url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        logger.error(repr(failure))
        storage = Storage(self.settings['storage'])
        storage.unlock_recipe_url(failure.request.url)

    def parse(self, response: Response, **kwargs):
        storage = Storage(self.settings['storage'])
        self.__fetched_count += 1
        try:
            item = RecipeItem(
                authors=[get_attribute(response.css('.recipe-page meta[itemprop=author]'), 'content', 'Food Network')],
                dateCreated=get_attribute(response.css('meta[itemprop=datePublished]'), 'content'),
                description=get_attribute(response.css('meta[name=description]'), 'content'),
                id=response.request.url,
                images=[response.css('meta[itemprop=image]').attrib['content'].strip()],
                ingredientsRaw=response.css('[itemprop=recipeIngredient]::text').getall(),
                instructionsRaw=response.css('[itemprop=recipeInstructions] p::text').getall(),
                language=response.css('meta[property="og:locale"]').attrib['content'].strip(),
                mainLink=response.url,
                sourceSite='Food Network',
                title=response.css('[itemprop=name]::text').get().strip()
            )
            if response.css('meta[itemprop=keywords]'):
                item.keywords = response.css('meta[itemprop=keywords]').attrib['content'].strip().split(', ')
                item.categories = item.keywords
            else:
                item.keywords = [item.title]
                item.categories = ['uncategorized']
            if response.css('meta[itemprop=cookTime]'):
                item.cookTime = parse_duration(response.css('meta[itemprop=cookTime]').attrib['content'].strip())
            if response.css('meta[itemprop=prepTime]'):
                item.prepTime = parse_duration(response.css('meta[itemprop=prepTime]').attrib['content'].strip())
            if response.css('meta[itemprop=recipeYield]'):
                item.yield_data = parse_yield(response.css('meta[itemprop=recipeYield]').attrib['content'].strip())
            item.suitableForDiet = tags_to_diet(item.keywords, DIET_TAG_MAP)
            logger.info(f'{response.url} is parsed successfully {self.__fetched_count} / {self.__total_count}')
            storage.mark_finished(response.request.url)
            yield item
        except Exception as ex:
            logger.error(f'translate url, {response.url},  {self.__fetched_count} / {self.__total_count}, '
                         f'error: {repr(ex)}')
            storage.unlock_recipe_url(response.request.url)
            raise ex
