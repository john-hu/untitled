from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import config, dataclass_json

from ..utils.parsers import as_array, isodate_2_isodatetime, parse_duration, parse_yield, split
from ..utils.schema_org import parse_authors, parse_nutrition_info, parse_suitable_for_diet, parse_video_urls, \
    parse_raw_ingredients, parse_raw_instructions, parse_image_urls, is_type


@dataclass
class RecipeURLItem:
    url: str


# This class is a subset of Recipe.json
@dataclass_json
@dataclass
# pylint: disable=too-many-instance-attributes
class RecipeItem:
    id: str
    mainLink: str
    title: str
    # `yield` is a reserved word. We use field to convert them.
    yield_data: Optional[dict] = field(metadata=config(field_name='yield'), default=None)
    language: str = None
    sourceSite: str = None
    authors: List[str] = None
    categories: Optional[List[str]] = None
    cookTime: int = None
    cookingMethods: List[str] = None
    cuisines: List[str] = None
    dateCreated: str = None
    dateModified: str = None
    description: str = None
    images: List[str] = None
    videos: List[str] = None
    ingredients: Optional[List[dict]] = None
    ingredientsRaw: Optional[List[str]] = None
    instructions: Optional[List[dict]] = None
    instructionsRaw: Optional[List[str]] = None
    nutrition: Optional[dict] = None
    keywords: Optional[List[str]] = None
    prepTime: int = None
    suitableForDiet: Optional[List[str]] = None
    version: str = 'raw'

    @staticmethod
    def fill_recipe_presets(item: 'RecipeItem') -> None:
        if not item.keywords:
            item.keywords = [item.title]
        if not item.categories:
            item.categories = ['uncategorized']

    # load data without the followings:
    # id, language, sourceSite, ingredients, instructions
    @staticmethod
    def from_schema_org(recipe: dict) -> Optional['RecipeItem']:
        if not recipe:
            return None
        elif not is_type(recipe, 'Recipe'):
            return None

        item = RecipeItem(
            authors=parse_authors(recipe.get('author', None)),
            categories=as_array(recipe.get('recipeCategory', None)),
            id=recipe.get('url', None),
            keywords=split(recipe.get('keywords', None)),
            title=recipe['name'],
            mainLink=recipe.get('url', None),
            version='raw'
        )
        item.cookTime = parse_duration(recipe.get('cookTime', None))
        item.cookingMethods = as_array(recipe.get('cookingMethod', None))
        item.cuisines = as_array(recipe.get('recipeCuisine', None))
        item.dateCreated = isodate_2_isodatetime(recipe.get('dateCreated', None))
        item.dateModified = isodate_2_isodatetime(recipe.get('dateModified', None))
        item.description = recipe.get('description', None)
        item.ingredientsRaw = parse_raw_ingredients(recipe.get('recipeIngredient', None))
        item.instructionsRaw = parse_raw_instructions(recipe.get('recipeInstructions', None))
        item.nutrition = parse_nutrition_info(recipe.get('nutrition', None))
        item.suitableForDiet = parse_suitable_for_diet(recipe.get('suitableForDiet', None))
        item.prepTime = parse_duration((recipe.get('prepTime', None)))
        item.yield_data = parse_yield(recipe.get('recipeYield', None))
        item.videos = parse_video_urls(recipe.get('video', None))
        item.images = parse_image_urls(recipe.get('image', None))
        # Some data containing nutrition. It's hard to parse it now. Just skip it at this version.
        RecipeItem.fill_recipe_presets(item)
        return item
