def safe_strftime(value, format='%m/%d/%Y %H:%M', on_none=''):
    if value is None:
        return on_none
    return value.strftime(format)