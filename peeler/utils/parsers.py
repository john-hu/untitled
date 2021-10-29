from typing import Dict, List, Optional

import isodate
from scrapy.http import Response


def parse_duration(text) -> int:
    return isodate.parse_duration(text).seconds


def get_attribute(element, attribute):
    return element.attrib[attribute].strip() if element else None


def parse_yield(yield_number: str) -> Optional[dict]:
    if not yield_number:
        return None
    try:
        return {'number': int(yield_number), 'unit': 'people'}
    except ValueError:
        return None


def tags_to_diet(tags: List[str], diet_map: Dict[str, str]) -> Optional[List[str]]:
    tags = [tag.lower() for tag in tags]
    result = []
    for (tag, diet) in diet_map.items():
        if tag in tags:
            result.append(diet)
    return result if result else None
