from urllib.parse import urljoin
from scrapy import Request, Spider
from scrapy.http import Response

from ..items import RecipeItem


# TODO: implement a way to stop requesting
class RecipeListSpider(Spider):
    name = 'recipe_list'
    allowed_domains = ['foodista.com']

    def start_requests(self):
        yield Request(url='https://www.foodista.com/community-recipes/?page=27', callback=self.parse)

    def parse(self, response: Response, **kwargs):
        all_hrefs = response.css('.view-display-id-community_recipes_page .views-row .views-field-title a')\
                            .xpath('@href').getall()
        for href in all_hrefs:
            item = RecipeItem()
            item['url'] = urljoin(response.url, href)
            yield item
        # find the next page url
        next_page = response.css('.pager .pager-next a').xpath('@href').get()
        yield Request(url=urljoin(response.url, next_page), callback=self.parse)
