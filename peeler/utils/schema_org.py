import json
import logging
import re
from typing import Callable, List, Optional, Union

from .parsers import MASS_REGEX_PARSER

logger = logging.getLogger(__name__)

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

SCHEMA_ORG_NS = ['https://schema.org', 'https://schema.org/', 'http://schema.org', 'http://schema.org/']


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
    for key in ret:
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


def parse_video_urls(video: Optional[Union[List[dict], List[str], dict]]) -> Optional[List[str]]:
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


def parse_image_urls(image: Optional[Union[List[str], dict, str]]) -> Optional[List[str]]:
    if not image:
        return None
    elif isinstance(image, list):
        ret = []
        for img in image:
            if isinstance(img, str):
                ret.append(img)
            elif isinstance(img, dict):
                if is_type(img, 'ImageObject', False) and ('contentUrl' in img or 'url' in img):
                    ret.append(img['contentUrl'] if 'contentUrl' in img else img['url'])
        return ret
    elif isinstance(image, str):
        return [image]
    elif isinstance(image, dict) and is_type(image, 'ImageObject', False) and ('contentUrl' in image or 'url' in image):
        return [image['contentUrl'] if 'contentUrl' in image else image['url']]
    else:
        return None


def parse_suitable_for_diet(data: Union[List[str], str]) -> Optional[List[str]]:
    if isinstance(data, str):
        return [DIET_MAP[data]] if data in DIET_MAP else None
    elif isinstance(data, list):
        ret = []
        for item in data:
            if data in DIET_MAP:
                ret.append(item)
        return ret if ret else None
    else:
        return None


def parse_raw_ingredients(data: Optional[Union[List[str], str]]) -> Optional[List[str]]:
    if not data:
        return None
    elif isinstance(data, list):
        return data
    else:
        return data.split('\n')


def expand_how_to_sections(section: dict, callback: Callable[[dict, int], None]) -> None:
    if section.get('@type') != 'HowToSection':
        return
    total_items = len(section.get('itemListElement'))
    for item in section.get('itemListElement'):
        if isinstance(item, dict) and item.get('@type') == 'HowToSection':
            expand_how_to_sections(item, callback)
        else:
            callback(item, total_items)


def parse_raw_instructions(data: Optional[Union[List[str], List[dict]]]) -> Optional[List[str]]:
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


def is_type(data: dict, schema_type: str, with_context: bool = True) -> bool:
    if with_context and not is_schema_org_context(data):
        return False
    return data.get('@type', None) == schema_type or schema_type in data.get('@type', [])


def is_schema_org_context(data: dict) -> bool:
    return '@context' in data and data['@context'] in SCHEMA_ORG_NS


def find_json_from_list(data: List[dict], schema_type: str) -> Optional[dict]:
    for single_item in data:
        if is_type(single_item, schema_type):
            return single_item
    return None


def find_json_from_graph(data: dict, schema_type: str) -> Optional[dict]:
    for item in data['@graph']:
        if is_type(item, schema_type, False):
            return data
    return None


def find_json_by_schema_org_type(json_texts: List[str], schema_type: str) -> Optional[dict]:
    # multiple ld+json case
    for json_text in json_texts:
        try:
            # Some data may contain `\n` or `\r` at the ld+json. It is not correct JSON. Replace the `[\r\n]` to space.
            data = json.loads(re.sub(r'[\r\n]', ' ', json_text))
            if isinstance(data, list):
                # Some website will give us a list of schema org data
                return find_json_from_list(data, schema_type)
            elif isinstance(data, dict) and is_schema_org_context(data):
                # If we have multiple data in a website, some website uses @graph to group them.
                if '@graph' in data and isinstance(data['@graph'], list):
                    return find_json_from_graph(data, schema_type)
                elif is_type(data, schema_type):
                    # single data case
                    return data
            else:
                logger.error(f'{repr(type(dict))} -> schema org context: {is_schema_org_context(data)}')
        except json.decoder.JSONDecodeError as json_error:
            logger.error('unable to decode json text', exc_info=json_error)

    return None
