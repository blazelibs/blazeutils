import warnings

from .spreadsheets import workbook_to_reader as _workbook_to_reader

warnings.warn('xlrd module deprecated, workbook_to_reader() moved to spreadsheets module',
              DeprecationWarning)

def workbook_to_reader(xlwt_wb):
    return _workbook_to_reader(xlwt_wb)


