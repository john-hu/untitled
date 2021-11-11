import logging
from abc import ABCMeta, abstractmethod

from scrapy import Request, Spider
from scrapy.http import Response

from .items import RecipeItem
from ..utils.storage import ParseState, Storage
from ..utils.validator import validate

logger = logging.getLogger(__name__)


class InvalidResponseData(Exception):
    def __init__(self, **kwargs):
        if 'field' in kwargs:
            self.field = kwargs['field']

    @staticmethod
    def check_and_raise(recipe: dict, key: str) -> None:
        if isinstance(recipe, dict):
            if key not in recipe or not recipe[key]:
                raise InvalidResponseData(field=key)


class BaseResultSpider(Spider, metaclass=ABCMeta):
    name = 'recipe_result'

    @staticmethod
    def fill_recipe_presets(item: RecipeItem):
        if not item.keywords:
            item.keywords = [item.title]
        if not item.categories:
            item.categories = ['uncategorized']

    @staticmethod
    def parse_html_language(response: Response):
        html = response.css('html')
        if 'xml:lang' in html.attrib:
            return html.attrib['xml:lang']
        elif 'lang' in html.attrib:
            return html.attrib['lang']
        else:
            return None

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__fetched_count = 0
        self.__total_count = 0

    def start_requests(self):
        storage = Storage(self.settings['storage'])
        urls = storage.lock_recipe_urls(self.settings['peel_count'])
        logger.info(f'locked urls count: {len(urls)}')
        self.__total_count = len(urls)
        for url in urls:
            yield Request(url=url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        logger.error(repr(failure))
        storage = Storage(self.settings['storage'])
        storage.unlock_recipe_url(failure.request.url)

    def parse(self, response: Response, **kwargs):
        storage = Storage(self.settings['storage'])
        self.__fetched_count += 1
        try:
            item = self.parse_response(response)
            validate(item.to_dict())
            yield item
            logger.info(f'{response.url} is parsed successfully {self.__fetched_count} / {self.__total_count}')
            storage.mark_finished(response.request.url)
        except InvalidResponseData as _invalid:
            logger.error(f'URL {response.url} does not have enough data')
            storage.mark_as(response.request.url, ParseState.WRONG_DATA)
            return
        except Exception as ex:
            logger.error(f'Parse url, {response.url},  {self.__fetched_count} / {self.__total_count}, '
                         f'error: {repr(ex)}')
            storage.unlock_recipe_url(response.request.url)
            raise ex

    @abstractmethod
    def parse_response(self, response: Response) -> RecipeItem:
        pass
