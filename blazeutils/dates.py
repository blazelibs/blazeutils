from __future__ import absolute_import
from __future__ import unicode_literals

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


def trim_mils(dobj, roundsecs=False):
    newdt = dt.datetime(dobj.year, dobj.month, dobj.day, dobj.hour, dobj.minute, dobj.second)
    if not roundsecs or dobj.microsecond < 500:
        return newdt
    return newdt + dt.timedelta(seconds=1)


def trim_seconds(dobj):
    return dt.datetime(dobj.year, dobj.month, dobj.day, dobj.hour, dobj.minute)
