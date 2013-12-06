from blazeutils.testing import emits_deprecation


class TestWorkbookToReader(object):

    @emits_deprecation('xlrd module deprecated, workbook_to_reader\(\) moved to spreadsheets module')
    def test_deprecation(self):
        from blazeutils.xlrd import workbook_to_reader
