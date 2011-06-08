from nose.tools import eq_
from blazeutils import tb_depth_in, traceback_depth
from blazeutils.testing import emits_deprecation

@emits_deprecation('.+its a bad idea')
def test_traceback_funcs():
    try:
        import somethingthatwontbethereihope
        assert False, 'expected import error'
    except ImportError:
        pass
    eq_(traceback_depth(), 0, msg='if this test fails, you probably have something wrapping __import__')

    try:
        from _bad_import import foobar
    except ImportError:
        pass
    eq_(traceback_depth(), 0)

    try:
        from _bad_import_deeper import foobar
    except ImportError:
        pass
    eq_(traceback_depth(), 1)

    assert tb_depth_in(1)
    assert tb_depth_in((0,1))
    assert not tb_depth_in((3,4))
