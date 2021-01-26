from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from blazeutils.error_handling import tb_depth_in, traceback_depth, _uie_matches


def test_traceback_funcs():
    try:
        import somethingthatwontbethereihope  # noqa
        assert False, 'expected import error'
    except ImportError:
        with pytest.warns(DeprecationWarning, match='.+its a bad idea'):
            assert traceback_depth() == 0, 'if this test fails, you probably have something ' \
                'wrapping __import__'

    try:
        from ._bad_import import foobar  # noqa
        assert False, 'expected Import Error'
    except ImportError:
        with pytest.warns(DeprecationWarning, match='.+its a bad idea'):
            assert traceback_depth() == 0

    try:
        from ._bad_import_deeper import foobar2  # noqa
        assert False, 'expected import error'
    except ImportError:
        with pytest.warns(DeprecationWarning, match='.+its a bad idea'):
            assert traceback_depth() == 1

        assert tb_depth_in(1)
        assert tb_depth_in((0, 1))
        assert not tb_depth_in((3, 4))


class TestRaiseUIE(object):

    def test_one(self):
        assert _uie_matches('minimal1.events', 'No module named events')
        assert _uie_matches('minimal1.events', "No module named 'events'")

    def test_two(self):
        assert _uie_matches('minimal2.components.internalonly.events',
                            'No module named internalonly.events')
        assert _uie_matches('minimal2.components.internalonly.events',
                            "No module named 'internalonly.events'")

    def test_end_matches_but_not_beginning(self):
        assert not _uie_matches('tcsdata.components.rem.model.orm',
                                'No module named tcdata.components.tcssite.model.orm')
        assert not _uie_matches('tcsdata.components.rem.model.orm',
                                "No module named 'tcdata.components.tcssite.model.orm'")

    def test_completely_different_exception(self):
        assert not _uie_matches('minimal2.components.internalonly.events',
                                'DLL load failed: The specified module could not be found.')
