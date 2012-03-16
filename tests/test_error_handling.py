from nose.tools import eq_
from blazeutils import tb_depth_in, traceback_depth
from blazeutils.error_handling import _uie_matches
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

class TestRaiseUIE(object):

    def test_one(self):
        assert _uie_matches('minimal1.events', 'No module named events')

    def test_two(self):
        assert _uie_matches('minimal2.components.internalonly.events', 'No module named internalonly.events')

    def test_end_matches_but_not_beginning(self):
        assert not _uie_matches('tcsdata.components.rem.model.orm', 'No module named tcdata.components.tcssite.model.orm')

