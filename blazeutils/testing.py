from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import datetime as dt
import difflib
import inspect
from io import StringIO
import logging
import re
import sys
import warnings

from blazeutils.log import clear_handlers_by_attr
from blazeutils.helpers import Tee, prettifysql
import six
from six.moves import zip as izip
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
            for w, m in izip(wcm, messages):
                count += 1
                assert m is not None, 'No message to match warning: %s' % w.message
                assert w is not None, 'No warning to match message #%s: %s' % (count, m)
                assert issubclass(w.category, DeprecationWarning), \
                    'DeprecationWarning not emitted, got %s type instead' % w.category
                assert re.search(m, str(w.message)), \
                    'Message regex "%s" did not match "%s"' % (m, w.message)
            return retval
    return decorate


def raises(arg1, arg2=None, re_esc=True, **kwargs):  # noqa
    """
        Decorate a test encorcing it emits the given Exception and message
        regex.

        Arguments to this decorator can be one or both of:

            A) Exception type or callable to validate the exception
            B) If A is an Exception type, then a message or regex to match against the string
            representation of the exception

        So, all the following are valid:

            @raises(AttributeError)
            @raises("object has no attribute 'foo'")
            @raises(AttributeError, "object has no attribute 'foo')
            @raises("^.+object has no attribute 'foo'", AttributeError)

            # with regex support
            @raises("^.+object has no attribute 'foo'", re_esc=False)

            # using custom exception validator
            @raises(my_custom_validator)

            my_custom_validator() should accept a single argument, the exception caught by @raises,
            and return True if the exception was expected and False otherwise

        @raises also supports examing arbitrary attributes on the exception for a given message
        by using keyword arguments:

            @raises(SomeException, foo='bar')

            This will ensure that the exception is of the SomeException type also that the exception
            has an attribute "foo" with a value of "bar."  No regex support currently for these
            messages.
    """
    exc_validator = None
    # if arg1 is callable, and not a class or, if it is a class, not a BaseException, assume
    # arg1 should be a validator of the exception
    if callable(arg1) and (not inspect.isclass(arg1) or not issubclass(arg1, BaseException)):
        exc_validator = arg1
        msgregex = None
        etype = None
    elif isinstance(arg1, six.string_types):
        msgregex = arg1
        etype = arg2
    elif isinstance(arg2, six.string_types):
        etype = arg1
        msgregex = arg2
    else:
        etype = arg1
        msgregex = None

    if re_esc and msgregex:
        msgregex = re.escape(msgregex)

    @wrapt.decorator
    def decorate(fn, instance, args, kw):
        try:
            fn(*args, **kw)
            assert False, '@raises: no exception raised in %s()' % fn.__name__
        except Exception as e:
            if exc_validator is not None and not exc_validator(e):
                raise
            if etype is not None and not isinstance(e, etype):
                raise
            if msgregex is not None and not re.search(msgregex, str(e)):
                raise
            for attrname, msg in six.iteritems(kwargs):
                if not hasattr(e, attrname):
                    print('@raises: exception missing "{0}" attribute'.format(attrname))
                    raise
                if getattr(e, attrname) != msg:
                    raise

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
