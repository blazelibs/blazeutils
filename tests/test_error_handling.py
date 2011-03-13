from nose.tools import eq_
from blazeutils import tb_depth_in, traceback_depth

def test_traceback_funcs():
    try:
        import foobar
    except ImportError:
        pass
    eq_(traceback_depth(), 0)
    
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