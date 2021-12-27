import logging
from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse

from scrapy import Request, Spider
from scrapy.exceptions import IgnoreRequest
from scrapy.http import Response
from scrapy.responsetypes import ResponseTypes

from ..items import RecipeItem
from ...utils.storage import ParseState, Storage
from ...utils.validator import validate

logger = logging.getLogger(__name__)


class InvalidResponseData(Exception):
    def __init__(self, **kwargs):
        super().__init__()
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
    def parse_html_language(response: Response):
        html = response.css('html')
        if 'xml:lang' in html.attrib:
            return html.attrib['xml:lang']
        elif 'lang' in html.attrib:
            return html.attrib['lang']
        else:
            return None

    @staticmethod
    def parse_site_name(response: Response) -> str:
        site_name = response.css('meta[property="og:site_name"]').attrib.get('content', None)
        if not site_name:
            site_name = urlparse(response.url).hostname
        return site_name

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.fetched_count = 0
        self.total_count = 0

    def start_requests(self):
        storage = Storage(self.settings['storage'])
        urls = storage.lock_recipe_urls(self.settings['peel_count'])
        logger.info(f'locked urls count: {len(urls)}')
        self.total_count = len(urls)
        for url in urls:
            yield Request(url=url, callback=self.parse, errback=self.handle_error)

    def handle_error(self, failure) -> None:
        logger.error(repr(failure))
        storage = Storage(self.settings['storage'])
        if failure.type == IgnoreRequest and 'Forbidden by robots.txt' in str(failure.value):
            logger.error(f'Forbidden, mark as error: {failure.request.url}')
            storage.mark_as(failure.request.url, ParseState.WRONG_DATA)
        else:
            logger.error(f'execute error, unlock: {failure.request.url}')
            storage.unlock_recipe_url(failure.request.url)

    def handle_not_html_error(self, response: Response) -> None:
        logger.error(f'url not HTML, mark as error: {response.request.url}')
        storage = Storage(self.settings['storage'])
        storage.mark_as(response.request.url, ParseState.WRONG_DATA)

    @staticmethod
    def is_parsable(response: Response) -> bool:
        types = ResponseTypes()
        return types.from_headers(response.headers) != Response

    def parse(self, response: Response, **kwargs):
        if not self.is_parsable(response):
            self.handle_not_html_error(response)
            return
        storage = Storage(self.settings['storage'])
        self.fetched_count += 1
        try:
            item = self.parse_response(response)
            validate(item.to_dict())
            yield item
            logger.info(f'{response.url} is parsed successfully {self.fetched_count} / {self.total_count}')
            storage.mark_finished(response.request.url)
        except InvalidResponseData as invalid:
            logger.error(f'URL {response.url} does not have enough data: {invalid.field}')
            storage.mark_as(response.request.url, ParseState.WRONG_DATA)
        except Exception as ex:  # pylint: disable=broad-except
            logger.error(f'Parse url, {response.url},  {self.fetched_count} / {self.total_count}, '
                         f'error: {repr(ex)}', exc_info=ex)
            storage.unlock_recipe_url(response.request.url)

    @abstractmethod
    def parse_response(self, response: Response) -> RecipeItem:
        pass
