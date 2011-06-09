import sys

from blazeutils.testing import raises

class TestRaisesDecorator(object):

    @raises(AttributeError)
    def test_arg1(self):
        assert sys.foo

    @raises("^.+object has no attribute 'foo'")
    def test_arg2(self):
        assert sys.foo

    @raises(AttributeError, "^.+object has no attribute 'foo'")
    def test_arg3(self):
        assert sys.foo

    @raises("^.+object has no attribute 'foo'", AttributeError)
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
            if "@raises: an exception was not raised" != str(e):
                raise
