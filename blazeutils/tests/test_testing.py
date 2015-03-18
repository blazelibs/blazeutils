import datetime as dt
import sys

import mock

from blazeutils.testing import raises, assert_equal_sql, assert_equal_txt, \
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


class TestRaisesDecorator(object):

    @raises(AttributeError)
    def test_arg1(self):
        assert sys.foo

    @raises("object has no attribute 'foo'")
    def test_arg2(self):
        assert sys.foo

    @raises(AttributeError, "object has no attribute 'foo'")
    def test_arg3(self):
        assert sys.foo

    @raises("object has no attribute 'foo'", AttributeError)
    def test_arg4(self):
        assert sys.foo

    @raises(_is_attribute_exception)
    def test_callable_validator(self):
        assert sys.foo

    def test_non_matching_message(self):
        try:
            @raises("foobar", AttributeError)
            def wrapper():
                assert sys.foo
            wrapper()
            assert False, '@raises hid the exception but shouldn\'t have'
        except AttributeError, e:
            if "'module' object has no attribute 'foo'" != str(e):
                raise

    def test_non_matching_type(self):
        try:
            @raises(ValueError, "^.+object has no attribute 'foo'")
            def wrapper():
                assert sys.foo
            wrapper()
            assert False, '@raises hid the exception but shouldn\'t have'
        except AttributeError, e:
            if "'module' object has no attribute 'foo'" != str(e):
                raise

    def test_callable_validator_returns_false(self):
        try:
            @raises(_is_attribute_exception)
            def wrapper():
                raise ValueError('test ve')
            wrapper()
            assert False, '@raises hid the exception but shouldn\'t have'
        except ValueError, e:
            if "test ve" != str(e):
                raise

    def test_no_exception_raised(self):
        try:
            @raises(ValueError, "^.+object has no attribute 'foo'")
            def wrapper():
                pass
            wrapper()
            assert False, '@raises should have complained that an exception was not raised'
        except AssertionError, e:
            if "@raises: no exception raised in wrapper()" != str(e):
                raise

    @raises('[with brackets]')
    def test_non_regex(self):
        raise Exception('[with brackets]')

    @raises(LikeWerkzeugExc, description='Foobar')
    def test_custom_attributes_ok(self):
        raise LikeWerkzeugExc('Foobar')

    def test_custom_attributes_missing(self):
        try:
            @raises(LikeWerkzeugExc, description='Foobar')
            def wrapper():
                raise Exception('baz')
            wrapper()
            assert False, '@raises should have complained that the exception was missing the description attribute'
        except Exception, e:
            if "baz" != str(e):
                raise

    def test_custom_attributes_fails(self):
        try:
            @raises(LikeWerkzeugExc, description='Foobar')
            def wrapper():
                raise LikeWerkzeugExc('baz')
            wrapper()
            assert False, '@raises should have complained that the description attribute did not match'
        except LikeWerkzeugExc, e:
            pass

def test_assert_equal_sql():
    s2 = s1 = """
    select foo,
    bar,
    baz from bill"""
    assert_equal_sql(s1, s2)

@raises(AssertionError, ".+!=", re_esc=False)
def test_assert_equal_sql():
    s2 = s1 = """
    select foo,
    bar,
    baz from bill"""
    s2 = s2[5:]
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
    except AssertionError, e:
        assert '-    line 25' in str(e)
        assert '+    line 2' in str(e)

class TestMockDateTime(object):

    @mock.patch('blazeutils_mock_date.dt_date')
    def test_mock_today(self, m_date):
        import blazeutils_mock_date
        mock_date_today(m_date, 2012)
        assert dt.date(2012, 1, 1) == blazeutils_mock_date.dt_date.today()

    @mock.patch('blazeutils_mock_date.dt_datetime')
    def test_mock_now(self, m_datetime):
        import blazeutils_mock_date
        mock_datetime_now(m_datetime, 2012)
        assert dt.datetime(2012, 1, 1, 0, 0, 0) == blazeutils_mock_date.dt_datetime.now()

    @mock.patch('blazeutils_mock_date.dt_datetime')
    def test_mock_utcnow(self, m_datetime):
        import blazeutils_mock_date
        mock_datetime_utcnow(m_datetime, 2012)
        assert dt.datetime(2012, 1, 1, 0, 0, 0), blazeutils_mock_date.dt_datetime.utcnow()
