from blazeutils.error_handling import _uie_matches


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
