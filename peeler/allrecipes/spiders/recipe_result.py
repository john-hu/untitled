import logging

from scrapy.http import Response

from ...scrapy_utils.base_spiders import BaseResultSpider
from ...scrapy_utils.items import RecipeItem
from ...utils.parsers import parse_duration, parse_yield
from ...utils.schema_org import find_json_by_schema_org_type

logger = logging.getLogger(__name__)


class RecipeResultSpider(BaseResultSpider):
    allowed_domains = ['allrecipes.com']
    json_css_path = 'head script[type="application/ld+json"]::text'

    def parse_response(self, response: Response) -> RecipeItem:
        recipe = find_json_by_schema_org_type(response.css(self.json_css_path).getall(), 'Recipe')
        item = RecipeItem(
            authors=[x.get("name", None) for x in recipe["author"]],
            categories=recipe.get("recipeCategory", None),
            cookTime=parse_duration(recipe.get("cookTime", None)),
            cuisines=recipe.get("recipeCuisine", None),
            dateCreated=recipe.get("datePublished", None),
            prepTime=parse_duration(recipe.get("prepTime", None)),
            description=recipe.get("description", None),
            id=response.xpath('//link[@rel="canonical"]/@href').extract_first(),
            images=[recipe["image"].get("url", None)],
            ingredientsRaw=recipe.get("recipeIngredient", None),
            instructionsRaw=[x.get("text", None) for x in recipe["recipeInstructions"]],
            keywords=[response.xpath('//h1/text()').get()],
            language=response.css('html').xpath('@lang').get(),
            mainLink=response.xpath('//link[@rel="canonical"]/@href').extract_first(),
            sourceSite=response.xpath('//meta[@property="og:site_name"]/@content').extract_first(),
            title=response.xpath('//h1/text()').get(),
            yield_data=parse_yield(recipe.get("recipeYield", None)),
            version="raw"
        )
        BaseResultSpider.fill_recipe_presets(item)
        return item
