import logging
from scrapy import Request, Spider
from scrapy.http import Response

from bs4 import BeautifulSoup
import requests

from ...scrapy_utils.items import RecipeURLItem
from ...utils.storage import Storage


logger = logging.getLogger(__name__)
STOP_REQUESTING_COUNT = 10
BASE_URL = 'https://www.allrecipes.com/sitemap'


def parse_sitemap():
    r = requests.get(f'{BASE_URL}.xml')
    sp = BeautifulSoup(r.text, 'lxml')
    links = sp.find_all('loc')
    recipes = []
    for link in links:
        if link.text.split('/')[-3] == 'recipe':
            r1 = requests.get(link.text)
            sp1 = BeautifulSoup(r1.text, 'lxml')
            recipe_links = sp1.find_all('loc')
            for recipe_link in recipe_links:
                recipes.append(recipe_link.text)
    return recipes


class RecipeListSpider(Spider):
    name = 'recipe_list'
    allowed_domains = ['allrecipes.com']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__empty_counter = 0

    def start_requests(self):
        yield Request(url=parse_sitemap(), callback=self.parse)

    def parse(self, response: Response, **kwargs):
        storage = Storage(self.settings['storage'])

        yield_count = 0
        if not storage.has_recipe_url(response.url):
            yield_count += 1
            yield RecipeURLItem(url=response.url)

        # reset the counter if we have at least one url found.
        if yield_count > 0:
            self.__empty_counter = 0
        # stop the process when the connecting empty request exceeds the maximum value.
        if self.__empty_counter > STOP_REQUESTING_COUNT:
            return
        # find the next page url
        # next_page = response.css('.pager .pager-next a').xpath('@href').get()
        yield Request(url=response.url, callback=self.parse)
