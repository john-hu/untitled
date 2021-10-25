from scrapy import Spider
from scrapy.http import Response


# TODO: implement this
class RecipeResultSpider(Spider):
    name = 'recipe_result'
    allowed_domains = ['foodista.com']

    def start_requests(self):
        pass

    def parse(self, response: Response, **kwargs):
        pass
