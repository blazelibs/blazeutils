from cStringIO import StringIO
import itertools
import logging
import re
import sys
import warnings

from blazeutils.decorators import decorator
from blazeutils.log import clear_handlers_by_attr
from blazeutils.helpers import Tee

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
        Decorate a test encorcing it emits the given DeprecationWarnings with
        the given messages in the given order.

        Note: requires Python 2.6 or later
    """
    @decorator
    def decorate(fn, *args, **kw):
        if sys.version_info < (2, 6):
            raise NotImplementedError('warnings.catch_warnings() is needed, but not available in Python versions < 2.6')
        with warnings.catch_warnings(record=True) as wcm:
            retval = fn(*args, **kw)
            count = 0
            for w, m in itertools.izip_longest(wcm, messages):
                count += 1
                assert m is not None, 'No message to match warning: %s' % w.message
                assert w is not None, 'No warning to match message #%s: %s' % (count, m)
                assert w.category is DeprecationWarning, 'DeprecationWarning not emitted, got %s type instead' % w.category
                assert re.search(m, str(w.message)), 'Message regex "%s" did not match %s' % (m, w.message)
            return retval
    return decorate


