import logging
import re

import requests
from bs4 import BeautifulSoup
from scrapy import Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeURLItem
from ...utils.storage import Storage

logger = logging.getLogger(__name__)
BASE_URL = 'https://www.allrecipes.com/sitemap'


def validate_link(link: str, domains: list):
    if isinstance(link, str):
        m = re.search(r'\w+.com', link)
        return m.group(0) in domains


def parse_sitemap(url):
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'lxml')
    links = sp.find_all('loc')
    recipes = []
    for link in links:
        if link.text.split('/')[-3] == 'recipe':
            recipes.append(link.text)
    return recipes


class RecipeListSpider(Spider):
    name = 'recipe_list'
    allowed_domains = ['allrecipes.com']
    sitemap = BASE_URL + '.xml'
    start_urls = parse_sitemap(sitemap)

    def parse(self, response: Response, **kwargs):
        storage = Storage(self.settings['storage'])

        yield_count = 0
        r1 = requests.get(response.url)
        sp1 = BeautifulSoup(r1.text, 'lxml')
        recipe_links = sp1.find_all('loc')
        for recipe_link in recipe_links:
            if validate_link(recipe_link.text, self.allowed_domains):
                if not storage.has_recipe_url(recipe_link.text):
                    yield_count += 1
                    yield RecipeURLItem(url=recipe_link.text)
            else:
                continue
