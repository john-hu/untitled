# pylint: disable=too-many-return-statements
def time_str_to_second(time_str: str) -> int:
    lower_str = time_str.lower()
    if lower_str == 'sec':
        return 1
    elif lower_str == 'secs':
        return 1
    elif lower_str == 'seconds':
        return 1
    elif lower_str == 'min':
        return 60
    elif lower_str == 'mins':
        return 60
    elif lower_str == 'minutes':
        return 60
    elif lower_str == 'hour':
        return 60 * 60
    elif lower_str == 'hours':
        return 60 * 60
    elif lower_str == 'hrs':
        return 60 * 60
    else:
        return 1
