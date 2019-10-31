from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import itertools
import inspect

import six

from blazeutils import curry


def posargs_limiter(func, *args):
    """ takes a function a positional arguments and sends only the number of
    positional arguments the function is expecting
    """
    posargs = inspect.getfullargspec(func)[0]
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


def compose(*functions):
    """Function composition on a series of functions.

    Remember that function composition runs right-to-left: `f . g . h = f(g(h(x)))`. As a unix
    pipeline, it would be written: `h | g | f`.

    From https://mathieularose.com/function-composition-in-python/.
    """
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, identity)


def len_iter(iterable):
    """An efficient implementation for finding the length of an iterable without needing to retain
    its contents in memory."""
    return sum(1 for _ in iterable)


def first_where(pred, iterable, default=None):
    """Returns the first element in an iterable that meets the given predicate.

    :param default: is the default value to use if the predicate matches none of the elements.
    """
    return next(six.moves.filter(pred, iterable), default)


def identity(x):
    """The identity function."""
    return x


def partition_iter(pred, iterable):
    """Partitions an iterable with a predicate into two iterables, one with elements satisfying
    the predicate and one with elements that do not satisfy it.

    :returns: a tuple (satisfiers, unsatisfiers).
    """
    left, right = itertools.tee(iterable, 2)
    return (
        (x for x in left if pred(x)),
        (y for y in right if not pred(y))
    )


def partition_list(pred, iterable):
    """Partitions an iterable with a predicate into two lists, one with elements satisfying
    the predicate and one with elements that do not satisfy it.

    .. note: this just converts the results of partition_iter to a list for you so that you don't
    have to in most cases using `partition_iter` is a better option.

    :returns: a tuple (satisfiers, unsatisfiers).
    """
    left, right = partition_iter(pred, iterable)
    return list(left), list(right)


def unzip(iterable):
    """Unzip/transpose an iterable of tuples into a tuple of lists.

    WARNING: When given an empty iterable, this returns an empty list instead of a tuple. If you
    need a consistent interface then do something like this:

        left, right = unzip(two_columned_list) or ([], [])
    """
    return list(map(list, list(six.moves.zip(*iterable))))


def flatten(iterable):
    """Takes an iterable of iterables and flattens it by one layer (e.g. [[1],[2]] becomes [1,2]).
    """
    return list(itertools.chain(*iterable))


@curry
def split_every(n, iterable):
    """Returns a generator that spits an iteratable into n-sized chunks. The last chunk may have
    less than n elements.

    See http://stackoverflow.com/a/22919323/503377."""
    items = iter(iterable)
    return itertools.takewhile(bool, (list(itertools.islice(items, n)) for _ in itertools.count()))


def unique(iterable, key=identity):
    """Yields all the unique values in an iterable maintaining order"""
    seen = set()
    for item in iterable:
        item_key = key(item)
        if item_key not in seen:
            seen.add(item_key)
            yield item
