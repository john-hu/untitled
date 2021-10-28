import logging
from urllib.parse import urljoin
from scrapy import Request, Spider
from scrapy.http import Response

from ...utils.storage import Storage
from ..items import RecipeURLItem


logger = logging.getLogger(__name__)
STOP_REQUESTING_COUNT = 10


class RecipeListSpider(Spider):
    name = 'recipe_list'
    allowed_domains = ['foodista.com']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__empty_counter = 0

    def start_requests(self):
        yield Request(url='https://www.foodista.com/community-recipes/', callback=self.parse)

    def parse(self, response: Response, **kwargs):
        all_hrefs = response.css('.view-display-id-community_recipes_page .views-row .views-field-title a')\
                            .xpath('@href').getall()
        storage = Storage(self.settings['storage'])
        yield_count = 0
        for href in all_hrefs:
            url = urljoin(response.url, href)
            # check the existence to know if we need to stop requesting
            if not storage.has_recipe_url(url):
                yield_count += 1
                yield RecipeURLItem(url=url)

        # reset the counter if we have at least one url found.
        if yield_count > 0:
            self.__empty_counter = 0
        # stop the process when the connecting empty request exceeds the maximum value.
        if self.__empty_counter > STOP_REQUESTING_COUNT:
            return
        # find the next page url
        next_page = response.css('.pager .pager-next a').xpath('@href').get()
        yield Request(url=urljoin(response.url, next_page), callback=self.parse)
