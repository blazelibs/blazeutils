# absolute import is necessary or datetime import will give
# blazeutils.datetime instead
from __future__ import absolute_import
import datetime as dt

def safe_strftime(value, format='%m/%d/%Y %H:%M', on_none=''):
    if value is None:
        return on_none
    return value.strftime(format)

def ensure_datetime(dobj, time_part=None):
    """
        Adds time part to dobj if its a date object, returns dobj
        untouched if its a datetime object.
    """
    if isinstance(dobj, dt.datetime):
        return dobj
    return dt.datetime.combine(dobj, time_part or dt.time())

def ensure_date(dobj):
    """
        removes time part from dobj if its a datetime object, returns dobj
        untouched if its a date object.
    """
    if isinstance(dobj, dt.datetime):
        return dobj.date()
    return dobj
