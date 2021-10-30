from typing import Dict, List, Optional

import isodate


def parse_duration(text) -> int:
    return isodate.parse_duration(text).seconds


def get_attribute(element, attribute, default_value: str = None) -> str:
    return element.attrib[attribute].strip() if element else default_value


def parse_yield(yield_number: str) -> Optional[dict]:
    if not yield_number:
        return None
    try:
        return {'number': int(yield_number), 'unit': 'people'}
    except ValueError:
        return None


def tags_to_diet(tags: List[str], diet_map: Dict[str, str]) -> Optional[List[str]]:
    if not tags:
        return None
    tags = [tag.lower() for tag in tags]
    result = []
    for (tag, diet) in diet_map.items():
        if tag in tags:
            result.append(diet)
    return result if result else None
