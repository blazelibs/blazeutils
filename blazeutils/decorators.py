from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools
from functools import partial
import inspect
import itertools
import logging
import time
from traceback import format_exc
import sys
import warnings

import wrapt
import six
from six.moves import range, map

log = logging.getLogger(__name__)


def format_argspec_plus(fn, grouped=True):
    """Returns a dictionary of formatted, introspected function arguments.

    A enhanced variant of inspect.formatargspec to support code generation.

    fn
       An inspectable callable or tuple of inspect getargspec() results.
    grouped
      Defaults to True; include (parens, around, argument) lists

    Returns:

    args
      Full inspect.formatargspec for fn
    self_arg
      The name of the first positional argument, varargs[0], or None
      if the function defines no positional arguments.
    apply_pos
      args, re-written in calling rather than receiving syntax.  Arguments are
      passed positionally.
    apply_kw
      Like apply_pos, except keyword-ish args are passed as keywords.

    Example::

      >>> format_argspec_plus(lambda self, a, b, c=3, **d: 123)
      {'args': '(self, a, b, c=3, **d)',
       'self_arg': 'self',
       'apply_kw': '(self, a, b, c=c, **d)',
       'apply_pos': '(self, a, b, c, **d)'}

    """
    warnings.warn('format_argspec_plus is deprecated and will be removed.', DeprecationWarning, 2)
    spec = callable(fn) and inspect.getargspec(fn) or fn
    args = inspect.formatargspec(*spec)
    if spec[0]:
        self_arg = spec[0][0]
    elif spec[1]:
        self_arg = '%s[0]' % spec[1]
    else:
        self_arg = None
    apply_pos = inspect.formatargspec(spec[0], spec[1], spec[2])
    defaulted_vals = spec[3] is not None and spec[0][0-len(spec[3]):] or ()
    apply_kw = inspect.formatargspec(spec[0], spec[1], spec[2], defaulted_vals,
                                     formatvalue=lambda x: '=' + x)
    if grouped:
        return dict(args=args, self_arg=self_arg,
                    apply_pos=apply_pos, apply_kw=apply_kw)
    else:
        return dict(args=args[1:-1], self_arg=self_arg,
                    apply_pos=apply_pos[1:-1], apply_kw=apply_kw[1:-1])


def unique_symbols(used, *bases):
    used = set(used)
    for base in bases:
        pool = itertools.chain((base,), map(lambda i: base + str(i), range(1000)))
        for sym in pool:
            if sym not in used:
                used.add(sym)
                yield sym
                break
        else:
            raise NameError("exhausted namespace for symbol base %s" % base)


def decorator(target):
    warnings.warn('decorator is deprecated and will be removed. Use wrapt.', DeprecationWarning, 2)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        return target(wrapped, *args, **kwargs)
    return wrapper


def _num_required_args(func):
    """ Number of args for func

        >>> def foo(a, b, c=None):
        ... return a + b + c

        >>> _num_required_args(foo)
        2

        >>> def bar(*args):
        ... return sum(args)

        >>> print(_num_required_args(bar))
        None

        borrowed from: https://github.com/pytoolz/toolz
    """
    try:
        spec = inspect.getfullargspec(func)
        if spec.varargs:
            return None
        num_defaults = len(spec.defaults) if spec.defaults else 0
        return len(spec.args) - num_defaults
    except TypeError:
        return None


class curry(object):
    """ Curry a callable function

        Enables partial application of arguments through calling a function with an
        incomplete set of arguments.

        >>> def mul(x, y):
        ... return x * y
        >>> mul = curry(mul)

        >>> double = mul(2)
        >>> double(10)
        20

        Also supports keyword arguments

        >>> @curry # Can use curry as a decorator
        ... def f(x, y, a=10):
        ... return a * (x + y)

        >>> add = f(a=1)
        >>> add(2, 3)
        5


        borrowed from: https://github.com/pytoolz/toolz

        See Also:
        toolz.curried - namespace of curried functions
        http://toolz.readthedocs.org/en/latest/curry.html
    """
    def __init__(self, func, *args, **kwargs):
        if not callable(func):
            raise TypeError("Input must be callable")

        self.func = func
        self.args = args
        self.keywords = kwargs if kwargs else None
        self.__doc__ = self.func.__doc__
        try:
            self.__name__ = self.func.__name__
        except AttributeError:
            pass

    def __str__(self):
        return str(self.func)

    def __repr__(self):
        return repr(self.func)

    def __call__(self, *args, **_kwargs):
        args = self.args + args
        if _kwargs:
            kwargs = {}
            if self.keywords:
                kwargs.update(self.keywords)
            kwargs.update(_kwargs)
        elif self.keywords:
            kwargs = self.keywords
        else:
            kwargs = {}

        try:
            return self.func(*args, **kwargs)
        except TypeError:
            required_args = _num_required_args(self.func)

            # If there was a genuine TypeError
            if required_args is not None and len(args) >= required_args:
                raise

            # If we only need one more argument
            if (required_args is not None and required_args - len(args) == 1):
                if kwargs:
                    return partial(self.func, *args, **kwargs)
                else:
                    return partial(self.func, *args)

            return curry(self.func, *args, **kwargs)


def deprecate(message):
    """
        Decorate a function to emit a deprecation warning with the given
        message.
    """
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        warnings.warn(message, DeprecationWarning, 2)
        return wrapped(*args, **kwargs)
    return wrapper


def exc_emailer(send_mail_func, logger=None, catch=Exception, print_to_stderr=True):
    """
        Catch exceptions and email them using `send_mail_func` which should
        accept a single string argument which will be the traceback to be
        emailed. Will re-raise original exception if calling `send_mail_func`
        raises an exception.

        Provide a logging.Logger instance for `logger` if desired (recommended).

        The exceptions this decorator handled can be adjusted by setting `catch`
        to an Exception class or tuple of exception classes that should be
        handled.

    """
    # if they don't give a logger, use our own
    if logger is None:
        logger = log

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        exc_info = None
        try:
            return wrapped(*args, **kwargs)
        except catch as e:
            body = format_exc()
            exc_info = sys.exc_info()
            error_msg = 'exc_mailer() caught an exception, email will be sent.'
            logger.exception(error_msg)
            if print_to_stderr:
                print(error_msg + '  ' + str(e), file=sys.stderr)
            try:
                send_mail_func(body)
            except Exception:
                logger.exception('exc_mailer(): send_mail_func() threw an exception, '
                                 'logging it & then re-raising original exception')
                six.reraise(exc_info[0], exc_info[1], exc_info[2])
        finally:
            # delete the traceback so we don't have garbage collection issues.
            # see warning at: http://docs.python.org/library/sys.html#sys.exc_info
            if exc_info is not None:
                del exc_info
    return wrapper


class Retry(object):
    def __init__(self, tries, exceptions, delay=0.1, logger=None, msg=None, level=logging.DEBUG):
        """
        Decorator for retrying a function if exception occurs

        tries -- num tries to repeat
        exceptions -- exceptions to catch, single Exception class or tuple of exceptions
        delay -- wait between retries
        logger -- python logger to write debug message to
        msg = a string that the exception must contain in order to be caught
        """
        self.tries = tries
        if isinstance(exceptions, Exception):
            self.exceptions = (exceptions, )
        else:
            self.exceptions = exceptions
        self.delay = delay
        if logger is not None:
            self.log = logger
        else:
            self.log = log

        self.log_level = level
        self.msg = msg

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapfn(*args, **kwargs):
            for try_count in range(self.tries):
                try:
                    return fn(*args, **kwargs)
                except self.exceptions as e:
                    if self.msg is not None and self.msg not in str(e):
                        raise

                    message = "Retry, exception: {}".format(e)
                    self.log.log(self.log_level, message)

                    if try_count == self.tries - 1:
                        # no tries left, reraise
                        raise

                    time.sleep(self.delay)

        return wrapfn
retry = Retry  # noqa: E305


class hybrid_method(object):
    """A decorator which allows definition of a Python object method with both
    instance-level and class-level behavior::

        class MethodClass(object):
            @hybrid_method
            def value(self):
                return 'instance level'

            @value.classmethod
            def value(self):
                return 'class level'

    Credit: SQLAlchemy
    """

    def __init__(self, func, class_method=None):
        self.instance_method = func
        self.class_method = class_method or func

    def __get__(self, instance, owner):
        if instance is None:
            return self.class_method.__get__(owner, owner.__class__)
        else:
            return self.instance_method.__get__(instance, owner)

    def classmethod(self, func):
        self.class_method = func
        return self


def memoize(method_to_wrap):
    """
        Currently only works on instance methods.  Designed for use with SQLAlchemy entities.  Could
        be updated in the future to be more flexible.

        class User(Base):
            __tablename__ = 'users'

            id = Column(Integer, primary_key=True)
            addresses = relationship("Address", backref="user")

            @memoize
            def address_count(self):
                return len(self.addresses)


        sqlalchemy.event.listen(User, 'expire', User.address_count.reset_memoize)


    """
    memoize_key = '_memoize_cache_{0}'.format(id(method_to_wrap))

    @wrapt.decorator
    def inner_memoize(wrapped, instance, args, kwargs):
        if instance is None and inspect.isclass(wrapped):
            # Wrapped function is a class and we are creating an
            # instance of the class. Don't support this case, just
            # return straight away.

            return wrapped(*args, **kwargs)

        # Retrieve the cache, attaching an empty one if none exists.
        cache = instance.__dict__.setdefault(memoize_key, {})

        # Now see if entry is in the cache and if it isn't then call
        # the wrapped function to generate it.

        try:
            key = (args, frozenset(kwargs.items()))
            return cache[key]

        except KeyError:
            result = cache[key] = wrapped(*args, **kwargs)
            return result

    def reset_memoize(target, *args):
        target.__dict__[memoize_key] = {}

    decorated = inner_memoize(method_to_wrap)
    decorated.reset_memoize = reset_memoize
    return decorated
