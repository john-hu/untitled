import logging
from urllib.parse import urljoin
from scrapy import Request, Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeURLItem
from ...utils.storage import Storage


logger = logging.getLogger(__name__)
STOP_REQUESTING_COUNT = 20


class RecipeListSpider(Spider):
    name = 'recipe_list'
    allowed_domains = ['yummly.co.uk']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__empty_counter = 0

    def start_requests(self):
        yield Request(url='https://www.yummly.co.uk/sitemap-en-GB-1.html', callback=self.parse)

    def parse(self, response: Response, **kwargs):
        all_hrefs = response.css('a[href]').xpath('@href').getall()
        storage = Storage(self.settings['storage'])
        yield_count = 0
        next_page = None
        for href in all_hrefs:
            if href.startswith('https://www.yummly.co.uk/recipe'):
                # check the existence to know if we need to stop requesting
                if not storage.has_recipe_url(href):
                    yield_count += 1
                    yield RecipeURLItem(url=href)
            elif not next_page:
                next_page = href

        # reset the counter if we have at least one url found.
        if yield_count > 0:
            self.__empty_counter = 0
        else:
            self.__empty_counter += 1

        # stop the process when the connecting empty request exceeds the maximum value.
        if self.__empty_counter > STOP_REQUESTING_COUNT:
            return
        # find the next page url
        yield Request(url=urljoin(response.url, next_page), callback=self.parse)
