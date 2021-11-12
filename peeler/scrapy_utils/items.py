from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json
from typing import List, Optional


@dataclass
class RecipeURLItem:
    url: str


# This class is a subset of Recipe.json that Foodista can fulfill, using the JSON naming convention
@dataclass_json
@dataclass
class RecipeItem:
    id: str
    language: str
    mainLink: str
    sourceSite: str
    title: str
    # `yield` is a reserved word. We use field to convert them.
    yield_data: Optional[dict] = field(metadata=config(field_name='yield'), default=None)
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
