from nose.tools import eq_
import xlwt

from blazeutils.spreadsheets import workbook_to_reader, XlwtHelper
from blazeutils.testing import emits_deprecation


class TestWorkbookToReader(object):

    def test_it(self):

        write_wb = xlwt.Workbook()
        ws = write_wb.add_sheet('Foo')
        ws.write(0, 0, 'bar')

        wb = workbook_to_reader(write_wb)
        sh = wb.sheet_by_name('Foo')
        eq_(sh.cell_value(rowx=0, colx=0), 'bar')


class TestWriter(object):

    @emits_deprecation('XlwtHelper has been renamed to Writer')
    def test_xlwt_helper_deprecation(self):
        XlwtHelper()
