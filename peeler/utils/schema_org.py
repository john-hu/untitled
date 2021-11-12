import json
from typing import List, Optional, Union

from .parsers import MASS_REGEX_PARSER

DIET_MAP = {'https://schema.org/DiabeticDiet': 'DiabeticDiet',
            'https://schema.org/GlutenFreeDiet': 'GlutenFreeDiet',
            'https://schema.org/HalalDiet': 'HalalDiet',
            'https://schema.org/HinduDiet': 'HinduDiet',
            'https://schema.org/KosherDiet': 'KosherDiet',
            'https://schema.org/LowCalorieDiet': 'LowCalorieDiet',
            'https://schema.org/LowFatDiet': 'LowFatDiet',
            'https://schema.org/LowLactoseDiet': 'LowLactoseDiet',
            'https://schema.org/LowSaltDiet': 'LowSaltDiet',
            'https://schema.org/VeganDiet': 'VeganDiet',
            'https://schema.org/VegetarianDiet': 'VegetarianDiet'}


def parse_nutrition_info(nutrition: Optional[dict]) -> Optional[dict]:
    if not nutrition:
        return None
    elif nutrition['@type'] != 'NutritionInformation':
        return None
    ret: dict = {
        "calories": None,
        "carbohydrateContent": None,
        "cholesterolContent": None,
        "fatContent": None,
        "fiberContent": None,
        "proteinContent": None,
        "saturatedFatContent": None,
        "servingSize": None,
        "sodiumContent": None,
        "sugarContent": None,
        "transFatContent": None,
        "unsaturatedFatContent": None,
    }
    for key in ret.keys():
        if key not in nutrition:
            continue
        match = MASS_REGEX_PARSER.match(nutrition[key])
        if not match:
            continue
        ret[key] = {'number': float(match.groups()[0]), 'unit': match.groups()[1]}

    return ret


def parse_authors(author: Union[List[dict], dict, str]) -> Optional[List[str]]:
    if not author:
        return None
    if isinstance(author, str):
        return [author]
    elif isinstance(author, list):
        return [item['name'] for item in author]
    elif isinstance(author, dict):
        return [author['name']]
    else:
        return None


def parse_video_urls(video: dict) -> Optional[List[str]]:
    if not video:
        return None
    elif video['@type'] != 'VideoObject':
        return None
    elif 'contentUrl' in video:
        return [video['contentUrl']]
    else:
        return None


def parse_suitable_for_diet(data: str) -> Optional[List[str]]:
    return [DIET_MAP[data]] if data in DIET_MAP else None


def find_json_by_schema_org_type(json_texts: List[str], schema_type: str) -> dict:
    for json_text in json_texts:
        data = json.loads(json_text)
        if data['@context'] == 'http://schema.org' and data['@type'] == schema_type:
            return data
