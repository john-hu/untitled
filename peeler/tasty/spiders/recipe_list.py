from bs4 import BeautifulSoup
from scrapy import Request, Spider
from scrapy.http import Response

from ...scrapy_utils.items import RecipeURLItem
from ...utils.storage import Storage


class RecipeListSpider(Spider):
    name = 'recipe_list'
    allowed_domains = ['tasty.co']

    def start_requests(self):
        yield Request(url='https://tasty.co/sitemaps/tasty/sitemap.xml', callback=self.parse)

    def parse(self, response: Response, **kwargs):
        sitemap = BeautifulSoup(response.text, 'lxml')
        storage = Storage(self.settings['storage'])
        for loc in sitemap.find_all('loc'):
            if not loc.text.startswith('https://tasty.co/recipe/'):
                continue
            # check the existence to know if we need to stop requesting
            if not storage.has_recipe_url(loc.textÎ):
                yield RecipeURLItem(url=loc.text)
