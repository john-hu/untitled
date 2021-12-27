import logging
from abc import abstractmethod
from typing import Generator, Union

import jsonschema
from scrapy.http import Response

from .base import BaseResultSpider, InvalidResponseData
from ..items import RecipeItem, RecipeURLItem
from ...utils.storage import ParseState, Storage
from ...utils.validator import validate

logger = logging.getLogger(__name__)


class GeneratorResultSpider(BaseResultSpider):
    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.ignore_validation_error = False

    def parse_response(self, response: Response) -> RecipeItem:
        # dummy override it and expose a new one
        pass

    @abstractmethod
    def yield_results(self, response: Response) -> Generator[Union[RecipeItem, RecipeURLItem], None, None]:
        pass

    def parse(self, response: Response, **kwargs):
        if not self.is_parsable(response):
            self.handle_not_html_error(response)
            return
        storage = Storage(self.settings['storage'])
        self.fetched_count += 1
        item_yield_count = 0
        url_yield_count = 0
        try:
            for item in self.yield_results(response):
                if isinstance(item, RecipeItem):
                    try:
                        validate(item.to_dict())
                        yield item
                        item_yield_count += 1
                    except jsonschema.ValidationError as ex:
                        if self.ignore_validation_error:
                            # pass the jsonschema validation error because this may be in the suggestion links
                            pass
                        else:
                            # raise error when the validation error is the main link
                            raise ex
                elif isinstance(item, RecipeURLItem) and not storage.has_recipe_url(item.url):
                    # a new url found, yield it as new url item
                    yield item
                    url_yield_count += 1
            yield_count = item_yield_count + url_yield_count
            if yield_count == 0:
                raise InvalidResponseData(field='empty_payload')
            logger.info(f'{response.url} yields {yield_count} - {self.fetched_count} / {self.total_count}')
            storage.mark_finished(response.request.url)
        except InvalidResponseData as invalid:
            logger.error(f'URL {response.url} does not have enough data: {invalid.field}')
            storage.mark_as(response.request.url, ParseState.WRONG_DATA)
            return
        except Exception as ex:
            logger.error(f'Parse url, {response.url},  {self.fetched_count} / {self.total_count}, '
                         f'error: {repr(ex)}')
            storage.unlock_recipe_url(response.request.url)
            raise ex
