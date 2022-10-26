import datetime as dt
import difflib
from io import StringIO
import logging
import re
import sys
import warnings

from blazeutils.decorators import deprecate
from blazeutils.log import clear_handlers_by_attr
from blazeutils.helpers import Tee, prettifysql
import wrapt


class LoggingHandler(logging.Handler):
    """ logging handler to check for expected logs when testing"""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        # have to setdefault in case there are custom levels
        key = record.levelname.lower()
        self.messages.setdefault(key, [])
        self.messages[key].append(record.getMessage())
        self.messages['all'].append(record.getMessage())

    def reset(self):
        self.all_index = 0
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
            'all': [],
        }

    @property
    def next(self):
        self.all_index += 1
        return self.current

    @property
    def current(self):
        return self.messages['all'][self.all_index]


def logging_handler(name=None, level=1):
    lh = LoggingHandler()
    lh.__blazeutils_testing__ = True
    lh.setLevel(level)
    if name:
        class NameFilter(logging.Filter):
            def filter(self, record):
                if record.name.startswith(self.name):
                    return True
                return False
        lh.addFilter(NameFilter(name))
        # set the level on the logger object so that it sends messages
        log = logging.getLogger(name)
        log.setLevel(level)
    logging.root.addHandler(lh)
    logging.root.setLevel(level)
    return lh


def clear_test_handlers():
    clear_handlers_by_attr('__blazeutils_testing__')


class StdCapture(object):

    def __init__(self):
        raise Exception('StdCapture wasn\'t easily converted to Python 3.  See comments in source.')
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        self.clear()

    def clear(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        sys.stdout = Tee(self.stdout, self.orig_stdout)
        sys.stderr = Tee(self.stderr, self.orig_stderr)

    def restore(self):
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr


class ListIO(object):
    def __init__(self):
        self.reset()

    def write(self, value):
        self.contents.append(value)

    def reset(self):
        self.contents = []
        self.index = 0

    def getvalue(self):
        return ''.join(self.contents)

    @property
    def next(self):
        self.index += 1
        return self.current

    @property
    def current(self):
        return self.contents[self.index]


@deprecate('The @emits_deprecation is deprecated. Use pytest.warns instead.')
def emits_deprecation(*messages):
    """
        Decorate a test enforcing it emits the given DeprecationWarnings with
        the given messages in the given order.

        Note: requires Python 2.6 or later
    """
    # DeprecationWarning is no longer loud by default in PY 2.7
    # we need to make it loud for @emits_deprecation below
    warnings.filterwarnings("default", category=DeprecationWarning)

    @wrapt.decorator
    def decorate(fn, instance, args, kw):
        if sys.version_info < (2, 6):
            raise NotImplementedError('warnings.catch_warnings() is needed, but not available '
                                      'in Python versions < 2.6')
        with warnings.catch_warnings(record=True) as wcm:
            retval = fn(*args, **kw)
            count = 0
            for w, m in zip(wcm, messages):
                count += 1
                assert m is not None, 'No message to match warning: %s' % w.message
                assert w is not None, 'No warning to match message #%s: %s' % (count, m)
                assert issubclass(w.category, DeprecationWarning), \
                    'DeprecationWarning not emitted, got %s type instead' % w.category
                assert re.search(m, str(w.message)), \
                    'Message regex "%s" did not match "%s"' % (m, w.message)
            return retval
    return decorate


def assert_equal_sql(sql, correct_sql):
    sql_split = prettifysql(sql)
    correct_sql_split = prettifysql(correct_sql)
    sql_diff = ''.join(list(
        difflib.unified_diff(correct_sql_split, sql_split)
    ))
    failure_message = "%r != %r\n" % (sql, correct_sql) + sql_diff
    assert sql == correct_sql, failure_message


def assert_equal_txt(txtblock, correct_txtblock):
    tb_split = txtblock.splitlines()
    ctb_split = correct_txtblock.splitlines()
    if tb_split != ctb_split:
        diff = '\n'.join(list(
            difflib.unified_diff(ctb_split, tb_split)
        ))
        assert False, 'txt blocks not equal, diff follows: \n' + diff


class FailLoader(object):
    """
        When an isntance is added to sys.meta_path, it will raise an ImportError
        when the given modules are imported.
    """
    def __init__(self, *modules):
        self.modules = list(modules)

    def find_module(self, fullname, path=None):
        if fullname in self.modules:
            raise ImportError('Debug import failure for %s' % fullname)

    def modules_from_package(self, package_name):
        for mod_name in sys.modules.keys():
            if mod_name == package_name or mod_name.startswith('{0}.'.format(package_name)):
                self.modules.append(mod_name)

    def delete_from_sys_modules(self):
        for mod_name in self.modules:
            del sys.modules[mod_name]


def mock_date_today(mock_obj, year, month=1, day=1):
    mock_obj.today.return_value = dt.date(year, month, day)
    mock_obj.side_effect = lambda *args, **kw: dt.date(*args, **kw)


def mock_datetime_now(mock_obj, year, month=1, day=1, hour=0, min=0, sec=0):
    mock_obj.now.return_value = dt.datetime(year, month, day, hour, min, sec)
    mock_obj.side_effect = lambda *args, **kw: dt.datetime(*args, **kw)


def mock_datetime_utcnow(mock_obj, year, month=1, day=1, hour=0, min=0, sec=0):
    mock_obj.utcnow.return_value = dt.datetime(year, month, day, hour, min, sec)
    mock_obj.side_effect = lambda *args, **kw: dt.datetime(*args, **kw)
