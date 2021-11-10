import re
import unicodedata
import logging
from datetime import datetime, timezone

from scrapy import Request, Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeItem
from ...utils.storage import Storage


logger = logging.getLogger(__name__)


def regex(rule, response):
    if isinstance(response, str):
        m = re.search(rule, response)
        if m:
            return m.group(0)
        else:
            return response
    return response


def convert_number(message):
    if message is None:
        return 0
    elif message == '':
        return 0
    else:
        try:
            return float(unicodedata.numeric(message))
        except TypeError:
            return int(message)


class RecipeResultSpider(Spider):
    name = 'recipe_result'
    allowed_domains = ['allrecipes.com']

    @staticmethod
    def retrieve_recipe_info(message):
        path = f'//div[@class="recipe-meta-item-header"][contains(text(), {message})]/following-sibling::div[1]/text()'
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
        print(f'this is url: {response.url}')
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
