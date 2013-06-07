from __future__ import absolute_import

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import xlrd

def workbook_to_reader(xlwt_wb):
    """
        convert xlwt Workbook instance to an xlrd instance for reading
    """
    fh = StringIO()
    xlwt_wb.save(fh)
    # prep for reading
    fh.seek(0)
    return xlrd.open_workbook(file_contents=fh.read())
