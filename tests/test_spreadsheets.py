from nose.tools import eq_
import xlwt

from blazeutils.spreadsheets import workbook_to_reader, XlwtHelper, http_headers
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


class TestHttpHeaders(object):

    def test_xls_filename(self):
        expect = {
            'Content-Type': 'application/vnd.ms-excel',
            'Content-Disposition': 'attachment; filename=foo.xls'
        }
        eq_(http_headers('foo.xls', randomize=False), expect)

    def test_xlsx_filename(self):
        expect = {
            'Content-Type': 'application/vnd.openxmlformats-officedocument'
                            '.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename=foo.xlsx'
        }
        eq_(http_headers('foo.xlsx', randomize=False), expect)

    def test_randomize(self):
        content_dispo = http_headers('foo.xlsx')['Content-Disposition']
        _, filename = content_dispo.split('=')
        intpart = filename.replace('foo-', '').replace('.xlsx', '')
        assert int(intpart) >= 1000000
