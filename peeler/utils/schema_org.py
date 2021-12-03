import json
from typing import Callable, List, Optional, Union

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

SCHEMA_ORG_NS = [
    'https://schema.org',
    'https://schema.org/',
    'http://schema.org',
    'http://schema.org/']


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
        ret[key] = {
            'number': float(
                match.groups()[0]),
            'unit': match.groups()[1]}

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


def parse_video_urls(
        video: Optional[Union[List[dict], List[str], dict]]) -> Optional[List[str]]:
    if not video:
        return None
    elif isinstance(video, dict) and video.get('@type', None) == 'VideoObject' and 'contentUrl' in video:
        return [video['contentUrl']]
    elif isinstance(video, list):
        ret = []
        for item in video:
            if isinstance(item, str):
                ret.append(item)
            elif isinstance(item, dict) and item.get('@type', None) == 'VideoObject' and 'contentUrl' in item:
                ret.append(item['contentUrl'])
        return ret
    else:
        return None


def parse_image_urls(
        image: Optional[Union[List[str], dict, str]]) -> Optional[List[str]]:
    if not image:
        return None
    elif isinstance(image, list):
        return image
    elif isinstance(image, str):
        return [image]
    elif isinstance(image, dict) and image.get('@type') == 'ImageObject' and 'contentUrl' in image:
        return [image['contentUrl']]
    else:
        return None


def parse_suitable_for_diet(data: str) -> Optional[List[str]]:
    return [DIET_MAP[data]] if data in DIET_MAP else None


def parse_raw_ingredients(
        data: Optional[Union[List[str], str]]) -> Optional[List[str]]:
    if not data:
        return None
    elif isinstance(data, list):
        return data
    else:
        return data.split('\n')


def expand_how_to_sections(
        section: dict, callback: Callable[[dict, int], None]) -> None:
    if section.get('@type') != 'HowToSection':
        return
    total_items = len(section.get('itemListElement'))
    for item in section.get('itemListElement'):
        if isinstance(item, dict) and item.get('@type') == 'HowToSection':
            expand_how_to_sections(item, callback)
        else:
            callback(item, total_items)


def parse_raw_instructions(
        data: Optional[Union[List[str], List[dict]]]) -> Optional[List[str]]:
    if not data:
        return None

    ret = []

    def inline_handle_section(subitem: dict, _total: int):
        if isinstance(subitem, str):
            ret.append(subitem)
        elif isinstance(subitem, dict) and subitem.get('@type') == 'HowToStep':
            ret.append(subitem.get('text'))

    for item in data:
        if isinstance(item, str):
            # handle str
            ret.append(item)
        elif isinstance(item, dict):
            # handle dict
            if item.get('@type') == 'HowToStep':
                ret.append(item.get('text'))
            if item.get('@type') == 'HowToSection':
                expand_how_to_sections(item, inline_handle_section)
    return ret


def find_json_by_schema_org_type(
        json_texts: List[str], schema_type: str) -> Optional[dict]:
    for json_text in json_texts:
        data = json.loads(json_text)
        if isinstance(data, list):
            for d in data:
                if d['@context'] in SCHEMA_ORG_NS and d['@type'] == schema_type:
                    return d
        elif data['@context'] in SCHEMA_ORG_NS and data['@type'] == schema_type:
            return data
    return None
