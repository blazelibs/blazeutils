import datetime as dt
from unittest import mock

import pytest

from blazeutils.testing import assert_equal_sql, assert_equal_txt, \
    mock_date_today, mock_datetime_now, mock_datetime_utcnow


class LikeWerkzeugExc(Exception):
    description = None

    def __init__(self, description=None):
        Exception.__init__(self)
        if description is not None:
            self.description = description

    def __str__(self):
        return '%d: %s' % (self.code, self.name)


def _is_attribute_exception(exc):
    return isinstance(exc, AttributeError)


def test_assert_equal_sql():
    s2 = s1 = """
    select foo,
    bar,
    baz from bill"""
    assert_equal_sql(s1, s2)


def test_assert_equal_sql_diff():
    s2 = s1 = """
    select foo,
    bar,
    baz from bill"""
    s2 = s2[5:]
    with pytest.raises(AssertionError, match=r'.+!='):
        assert_equal_sql(s1, s2)


def test_assert_equal_txt():
    s1 = """
    line 1
    line 2
    line 3"""
    assert_equal_txt(s1, s1)

    s2 = """
    line 1
    line 25
    line 3"""

    try:
        assert_equal_txt(s1, s2)
        assert False, 'expected exception'
    except AssertionError as e:
        assert '-    line 25' in str(e)
        assert '+    line 2' in str(e)


class TestMockDateTime(object):

    @mock.patch('blazeutils.tests.date_imports.dt_date')
    def test_mock_today(self, m_date):
        from . import date_imports
        mock_date_today(m_date, 2012)
        assert dt.date(2012, 1, 1) == date_imports.dt_date.today()

    @mock.patch('blazeutils.tests.date_imports.dt_datetime')
    def test_mock_now(self, m_datetime):
        from . import date_imports
        mock_datetime_now(m_datetime, 2012)
        assert dt.datetime(2012, 1, 1, 0, 0, 0) == date_imports.dt_datetime.now()

    @mock.patch('blazeutils.tests.date_imports.dt_datetime')
    def test_mock_utcnow(self, m_datetime):
        from . import date_imports
        mock_datetime_utcnow(m_datetime, 2012)
        assert dt.datetime(2012, 1, 1, 0, 0, 0), date_imports.dt_datetime.utcnow()
