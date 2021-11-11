from datetime import datetime
from typing import Dict, List, Optional

import isodate


def get_attribute(element, attribute, default_value: str = None) -> str:
    return element.attrib[attribute].strip() if element else default_value


def isodate_2_isodatetime(date: str) -> Optional[str]:
    if not date:
        return date
    parsed_date = isodate.parse_date(date)
    return datetime.combine(parsed_date, datetime.min.time()).isoformat(timespec='seconds')


def parse_duration(text) -> int:
    return isodate.parse_duration(text).seconds if text else None


def parse_yield(yield_number: str) -> Optional[dict]:
    if not yield_number:
        return None
    try:
        return {'number': int(yield_number), 'unit': 'people'}
    except ValueError:
        return None


def split(text: str, splitter: str = ', ') -> List[str]:
    if isinstance(text, list):
        return text
    return [] if not text else text.split(splitter)


def tags_to_diet(tags: List[str], diet_map: Dict[str, str]) -> Optional[List[str]]:
    if not tags:
        return None
    tags = [tag.lower() for tag in tags]
    result = []
    for (tag, diet) in diet_map.items():
        if tag in tags:
            result.append(diet)
    return result if result else None
