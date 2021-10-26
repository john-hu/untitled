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
    authors: List[str]
    categories: List[str]
    dateCreated: str
    description: str
    id: str
    images: List[str]
    ingredientsRaw: List[str]
    instructionsRaw: List[str]
    keywords: List[str]
    language: str
    mainLink: str
    title: str
    # `yield` is a reserved word. We use field to convert them.
    yield_data: Optional[dict] = field(metadata=config(field_name='yield'))
    version: str = 'raw'
    sourceSite: str = 'Foodista'
    suitableForDiet: Optional[List[str]] = None
