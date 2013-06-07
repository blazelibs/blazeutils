from nose.tools import eq_
import xlwt

from blazeutils.xlrd import workbook_to_reader

class TestWorkbookToReader(object):

    def test_it(self):

        write_wb = xlwt.Workbook()
        ws = write_wb.add_sheet('Foo')
        ws.write(0,0,'bar')

        wb = workbook_to_reader(write_wb)
        sh = wb.sheet_by_name('Foo')
        eq_(sh.cell_value(rowx=0,colx=0), 'bar')
