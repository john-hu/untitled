import json
import logging
from urllib.parse import urljoin

from scrapy import Request, Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeURLItem
from ...utils.storage import Storage

logger = logging.getLogger(__name__)
ADVANCED_SEARCH_PAGE = 'https://foodnetwork.co.uk/recipe-search/'


class RecipeListSpider(Spider):
    name = 'recipe_list'
    allowed_domains = ['foodnetwork.co.uk', 'uk-api.loma-cms.com']

    def start_requests(self):
        yield Request(url=ADVANCED_SEARCH_PAGE, callback=self.base_page)

    def base_page(self, response: Response, **kwargs):
        if response.status != 200:
            return

        yield Request(
            url='https://uk-api.loma-cms.com/feloma/search/page/' +
                '?environment=foodnetwork&pageType=recipepage&page_size=250&filter[attribute.difficulty]=1',
            callback=self.parse)
        yield Request(
            url='https://uk-api.loma-cms.com/feloma/search/page/' +
                '?environment=foodnetwork&pageType=recipepage&page_size=250&filter[attribute.difficulty]=3',
            callback=self.parse)
        yield Request(
            url='https://uk-api.loma-cms.com/feloma/search/page/' +
                '?environment=foodnetwork&pageType=recipepage&page_size=250&filter[attribute.difficulty]=5',
            callback=self.parse)

    def parse(self, response: Response, **kwargs):
        if response.status != 200:
            logger.error(f'response error, {response.status} {response.text}')
            return
        search_result = json.loads(response.text)
        data = search_result.get('data', [])
        logger.info(f'{response.url} results {len(data)}')
        storage = Storage(self.settings['storage'])
        yield_count = 0
        for item in data:
            if item.get('type') != 'recipepage':
                continue
            parent_slug = item.get('parentSlug', '')
            slug = item['slug']
            url = urljoin(
                'https://foodnetwork.co.uk/',
                urljoin(
                    f'{parent_slug}/',
                    f'{slug}/'))
            # check the existence to know if we need to stop requesting
            if not storage.has_recipe_url(url):
                yield_count += 1
                yield RecipeURLItem(url=url)
        logger.info(
            f'total: {len(data)}, yields: {yield_count}, duplicated: {len(data) - yield_count}')
        # find the next page url
        next_page = search_result.get('meta', {}).get('nextPage', None)
        if next_page:
            # change the referer to make uk-api.loma-cms.com feel we are from
            # foodnetwork search page
            headers = {'referer': ADVANCED_SEARCH_PAGE}
            yield Request(url=next_page, callback=self.parse, headers=headers)
