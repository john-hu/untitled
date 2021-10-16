import re

# copied from https://stackoverflow.com/a/12982689
CLEANER = re.compile('<.*?>')


def clean_html(raw_html: str) -> str:
    pure_text = re.sub(CLEANER, '', raw_html)
    return pure_text
