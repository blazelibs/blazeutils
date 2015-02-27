import xlwt

from blazeutils.testing import emits_deprecation


class TestWorkbookToReader(object):

    @emits_deprecation('xlrd module deprecated, workbook_to_reader\(\) moved to spreadsheets module')
    def test_it(self):
        from blazeutils.xlrd import workbook_to_reader

        write_wb = xlwt.Workbook()
        ws = write_wb.add_sheet('Foo')
        ws.write(0, 0, 'bar')

        wb = workbook_to_reader(write_wb)
        sh = wb.sheet_by_name('Foo')
        assert sh.cell_value(rowx=0, colx=0) == 'bar'
