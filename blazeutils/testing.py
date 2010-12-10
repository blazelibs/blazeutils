import sys
import logging
from cStringIO import StringIO
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
