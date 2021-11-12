import logging
import re
import unicodedata

from scrapy import Request, Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeItem
from ...utils.storage import Storage

logger = logging.getLogger(__name__)


def regex(rule, response):
    if not isinstance(response, str):
        return response
    m = re.search(rule, response)
    return m.group(0) if m else ''


def convert_number(message):
    if not message:
        return 0
    else:
        fraction_message = regex(r'([\u00BC~\u00BE]+|[\u2150~\u215F]+)', message)
        fraction_message = 0 if not fraction_message else float(unicodedata.numeric(fraction_message))
        num_message = regex(r'\d+', message)
        num_message = 0 if not num_message else int(num_message)
        return fraction_message + num_message if fraction_message != num_message else fraction_message


class RecipeResultSpider(Spider):
    name = 'recipe_result'
    allowed_domains = ['allrecipes.com']

    @staticmethod
    def retrieve_recipe_info(message):
        path = f'//div[@class="recipe-meta-item-header"][contains(text(),"{message}")]/following-sibling::div[1]/text()'
        return path

    @staticmethod
    def retrieve_ingredient_info(response):
        info_aggs = []
        for ingredient_info in response.css('.ingredients-item'):
            info_agg = {
                'name': ingredient_info.css('.checkbox-list-input').xpath('@data-ingredient').get(),
                'size': {
                    'number': convert_number(
                        ingredient_info.css('.checkbox-list-input').xpath('@data-quantity').get()),
                    'unit': ingredient_info.css('.checkbox-list-input').xpath('@data-unit').get()
                }
            }
            info_aggs.append(info_agg)
        return info_aggs

    @staticmethod
    def retrieve_step_info(response):
        info_aggs = []
        for step_info in response.css('.subcontainer.instructions-section-item'):
            info_agg = {
                'id': regex(r'\d', step_info.css('.checkbox-list-text::text').get()),
                'equipments': [],
                'language': response.css('html').xpath('@lang').get(),
                'text': step_info.css('p::text').get()
            }
            info_aggs.append(info_agg)
        return info_aggs

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
                authors=[response.css('.author-name-title .linkHoverStyle::text').getall()],
                categories=response.css('.breadcrumbs__title::text')[2].get(),
                cookTime=convert_number(
                    regex(r'\d+', response.xpath(self.retrieve_recipe_info('cook:')).extract_first())),
                description=response.xpath('//meta[@name="description"]/@content').extract_first(),
                id=response.xpath('//link[@rel="canonical"]/@href').extract_first(),
                images=[response.css('.recipe-review-image-wrapper noscript img').xpath('@src').get(0)],
                ingredients=self.retrieve_ingredient_info(response),
                instructions=self.retrieve_step_info(response),
                keywords=[response.xpath('//h1/text()').get()],
                language=response.css('html').xpath('@lang').get(),
                mainLink=response.xpath('//link[@rel="canonical"]/@href').extract_first(),
                sourceSite=response.xpath('//meta[@property="og:site_name"]/@content').extract_first(),
                title=response.xpath('//h1/text()').get()
            )
            logger.info(f'{response.url} is parsed successfully')
            yield item
            storage.mark_finished(response.request.url)
        except Exception as ex:
            logger.error(f'translate url, {response.url}, error: {repr(ex)}')
            storage.unlock_recipe_url(response.request.url)
            raise ex
