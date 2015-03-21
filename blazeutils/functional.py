from __future__ import absolute_import
from __future__ import unicode_literals

import inspect
import functools


def posargs_limiter(func, *args):
    """ takes a function a positional arguments and sends only the number of
    positional arguments the function is expecting
    """
    posargs = inspect.getargspec(func)[0]
    length = len(posargs)
    if inspect.ismethod(func):
        length -= 1
    if length == 0:
        return func()
    return func(*args[0:length])


class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    from: http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
