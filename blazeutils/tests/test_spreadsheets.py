from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import six

from blazeutils.spreadsheets import workbook_to_reader, XlwtHelper, http_headers, xlsx_to_reader
from blazeutils.testing import emits_deprecation


class TestWorkbookToReader(object):

    @pytest.mark.skipif(not six.PY2, reason="xlwt only works on Python 2")
    def test_xlwt_to_reader(self):
        import xlwt
        write_wb = xlwt.Workbook()
        ws = write_wb.add_sheet('Foo')
        ws.write(0, 0, 'bar')

        wb = workbook_to_reader(write_wb)
        sh = wb.sheet_by_name('Foo')
        assert sh.cell_value(rowx=0, colx=0) == 'bar'


class TestXlsxToReader(object):

    def test_xlsx_to_reader(self):
        import xlsxwriter
        write_wb = xlsxwriter.Workbook()
        ws = write_wb.add_worksheet('Foo')
        ws.write(0, 0, 'bar')

        wb = xlsx_to_reader(write_wb)
        sh = wb.sheet_by_name('Foo')
        assert sh.cell_value(rowx=0, colx=0) == 'bar'


class TestWriter(object):

    @emits_deprecation('XlwtHelper has been renamed to Writer')
    @pytest.mark.skipif(not six.PY2, reason="xlwt only works on Python 2")
    def test_xlwt_helper_deprecation(self):
        XlwtHelper()


class TestHttpHeaders(object):

    def test_xls_filename(self):
        expect = {
            'Content-Type': 'application/vnd.ms-excel',
            'Content-Disposition': 'attachment; filename=foo.xls'
        }
        assert http_headers('foo.xls', randomize=False), expect

    def test_xlsx_filename(self):
        expect = {
            'Content-Type': 'application/vnd.openxmlformats-officedocument'
                            '.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename=foo.xlsx'
        }
        assert http_headers('foo.xlsx', randomize=False) == expect

    def test_randomize(self):
        content_dispo = http_headers('foo.xlsx')['Content-Disposition']
        _, filename = content_dispo.split('=')
        intpart = filename.replace('foo-', '').replace('.xlsx', '')
        assert int(intpart) >= 1000000
