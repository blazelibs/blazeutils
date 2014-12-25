Recent Changelog
----------------

This is the most recent activity.  See `changelog-archive.rst` in the source distribution
for older changelog notes.

0.4.4 released 2014-12-25
================================

- changed how the version string is determined in __init__.py
- archive old changelog notes

0.4.3 released 2014-12-16
================================

- add xlsx_to_strio() and WriterX.mwrite()

0.4.2 released 2014-12-08
================================

- fix wrong dates for 0.4.0 and 0.4.1 releases in changelog
- add roundsecs argument to dates.trim_mils
- updates to spreadsheets module including .xlsx file support

    - xlsx_to_reader(): converts xlsxwriter.Workbook instance to xlrd reader
    - WriterX: like Writer but for xlsxwriter Worksheets, API is slightly different and won't have
      any faculties for style management like Writer does.
    - Reader: gets a .from_xlsx() method
    - http_headers(): utility function to help when sending files as HTTP response

0.4.1 released 2014-05-17
================================

- fix packaging issue

0.4.0 released 2014-05-17
================================

- testing.raises() gets support for custom exception validators, docstring updated w/ usage
- decorators.curry() use a different approach so multiple curried functions can be used
- add decorators.hybrid_method() ala SQLAlchemy
- add decorators.memoize() primarily for SQLAlchemy method caching
- BC break: .decorators now uses 'wrapt' so that is a new dependency
