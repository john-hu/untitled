import logging
from typing import Generator, List, Optional, Union
from urllib.parse import urldefrag, urljoin, urlparse

from scrapy import Request
from scrapy.http import Response

from ...scrapy_utils.spiders.generator_base import GeneratorResultSpider
from ...scrapy_utils.items import RecipeItem, RecipeURLItem
from ...utils.schema_org import find_json_by_schema_org_type

logger = logging.getLogger(__name__)


class GeneralResultSpider(GeneratorResultSpider):
    name = 'general_result'
    json_css_path = 'script[type="application/ld+json"]::text'

    @staticmethod
    def parse_raw_recipe(recipe: dict, language: str, site_name: str, url: Optional[str]):
        item = RecipeItem.from_schema_org(recipe)
        if not item:
            return None
        item.language = language
        item.sourceSite = site_name
        if not recipe.get('url', None) and url:
            item.id = url
            item.mainLink = url
        return item

    def start_requests(self) -> None:
        init_url = self.settings.get('init_url', None)
        if init_url:
            yield Request(url=init_url, callback=self.parse, errback=self.handle_error)
        else:
            yield from super().start_requests()

    def parse_recipe(self, response: Response, recipe_language: str, site_name: str) -> Generator[
                     Union[RecipeItem, RecipeURLItem], None, None]:
        # if recipe found, yield it
        recipe = find_json_by_schema_org_type(response.css(self.json_css_path).getall(), 'Recipe')
        self.ignore_validation_error = True
        if recipe:
            item = self.parse_raw_recipe(recipe, recipe_language, site_name, response.request.url)
            if item:
                yield item

    def parse_item_list_recipes(self, response: Response, recipe_language: str, site_name: str) -> Generator[
                                Union[RecipeItem, RecipeURLItem], None, None]:
        # if item list found, yield it
        item_list = find_json_by_schema_org_type(response.css(self.json_css_path).getall(), 'ItemList')
        if item_list:
            self.ignore_validation_error = True
            for recipe in item_list.get('itemListElement', []):
                # parse recipe type only
                if recipe.get('@type') == 'Recipe' and recipe.get('url', None):
                    # We should put the url into database for detailed parser.
                    yield self.parse_raw_recipe(recipe, recipe_language, site_name, None)

    @staticmethod
    def parse_anchor(response: Response) -> Generator[RecipeURLItem, None, None]:
        # We only emit url within the same site and not just hash changed link
        all_hrefs: List[str] = response.css('a::attr(href)').getall()
        current_hostname = urlparse(response.url).hostname
        current_defrag_url = urldefrag(response.url).url
        for href in all_hrefs:
            resolved_url = urljoin(response.url, href)
            resolved_hostname = urlparse(resolved_url).hostname
            resolved_defrag_url = urldefrag(resolved_url).url
            if resolved_hostname == current_hostname and current_defrag_url != resolved_defrag_url:
                yield RecipeURLItem(url=resolved_url)

    def yield_results(self, response: Response) -> Generator[Union[RecipeItem, RecipeURLItem], None, None]:
        recipe_language = self.parse_html_language(response)
        site_name = self.parse_site_name(response)
        logger.info(f'site: {site_name} in {recipe_language}')
        yield from self.parse_recipe(response, recipe_language, site_name)
        yield from self.parse_item_list_recipes(response, recipe_language, site_name)
        yield from self.parse_anchor(response)
