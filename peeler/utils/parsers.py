import re
from datetime import datetime
from typing import Dict, List, Optional, Union

import isodate

MASS_REGEX_PARSER = re.compile(r'(\d+)[^\S\n\r]+(\w+)')


def get_attribute(element, attribute, default_value: str = None) -> str:
    return element.attrib[attribute].strip() if element else default_value


def isodate_2_isodatetime(date: str) -> Optional[str]:
    if not date:
        return date
    parsed_date = isodate.parse_date(date)
    return datetime.combine(parsed_date, datetime.min.time()
                            ).isoformat(timespec='seconds')


def parse_duration(text) -> int:
    return isodate.parse_duration(text).seconds if text else None


def parse_yield(
        yield_number: Optional[Union[str, int, float]]) -> Optional[dict]:
    if not yield_number:
        return None
    elif isinstance(yield_number, int):
        return {'number': int(yield_number), 'unit': 'people'}
    elif isinstance(yield_number, float):
        return {'number': yield_number, 'unit': 'people'}
    elif not isinstance(yield_number, str):
        return None
    # try regex
    match = MASS_REGEX_PARSER.match(yield_number)
    if match:
        return {'number': int(match.groups()[0]), 'unit': match.groups()[1]}
    # try convert to int directly
    try:
        return {'number': int(yield_number), 'unit': 'people'}
    except ValueError:
        return None


def split(text: Optional[str], splitter: str = ' ') -> List[str]:
    if not text:
        return []
    elif isinstance(text, list):
        return text
    else:
        return [] if not text else text.replace(
            ', ', ' ').replace(',', ' ').split(splitter)


def as_array(text: Optional[Union[List[str], str]]) -> Optional[List[str]]:
    if not text:
        return None
    elif isinstance(text, list):
        return text
    elif isinstance(text, str):
        return [text]
    else:
        return None


def tags_to_diet(tags: List[str], diet_map: Dict[str,
                 str]) -> Optional[List[str]]:
    if not tags:
        return None
    tags = [tag.lower() for tag in tags]
    result = []
    for (tag, diet) in diet_map.items():
        if tag in tags:
            result.append(diet)
    return result if result else None
