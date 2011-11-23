import sys

from blazeutils.testing import raises, assert_equal_sql

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
