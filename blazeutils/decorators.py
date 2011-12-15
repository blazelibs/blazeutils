import functools
from functools import update_wrapper
import inspect, itertools
import logging
import time
from traceback import format_exc
import sys
import warnings

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
        pool = itertools.chain((base,),
                               itertools.imap(lambda i: base + str(i),
                                              xrange(1000)))
        for sym in pool:
            if sym not in used:
                used.add(sym)
                yield sym
                break
        else:
            raise NameError("exhausted namespace for symbol base %s" % base)

def decorator(target):
    """A signature-matching decorator factory."""

    def decorate(fn):
        spec = inspect.getargspec(fn)
        names = tuple(spec[0]) + spec[1:3] + (fn.func_name,)
        targ_name, fn_name = unique_symbols(names, 'target', 'fn')

        metadata = dict(target=targ_name, fn=fn_name)
        metadata.update(format_argspec_plus(spec, grouped=False))

        code = 'lambda %(args)s: %(target)s(%(fn)s, %(apply_kw)s)' % (
                metadata)
        decorated = eval(code, {targ_name:target, fn_name:fn})
        decorated.func_defaults = getattr(fn, 'im_func', fn).func_defaults
        return update_wrapper(decorated, fn)
    return update_wrapper(decorate, target)

def curry(fn, *args, **kwargs):
    """
    Decorator that returns a function that keeps returning functions
    until all arguments are supplied; then the original function is
    evaluated.
    """
    argscount = fn.func_code.co_argcount
    cargs = []
    def tocall(*args):
        cargs = tocall.cargs + list(args)
        tocall.cargs = cargs
        if len(tocall.cargs) < argscount:
            return tocall
        else:
            fnargs = tuple(tocall.cargs)
            tocall.cargs = []
            return fn(*fnargs)
    tocall.cargs = cargs
    return tocall

def deprecate(message):
    """
        Decorate a function to emit a deprecation warning with the given
        message.
    """
    @decorator
    def decorate(fn, *args, **kw):
        warnings.warn(message, DeprecationWarning, 2)
        return fn(*args, **kw)
    return decorate

def exc_emailer(send_mail_func, logger=None, catch=Exception):
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

    @decorator
    def decorate(fn, *args, **kwargs):
        exc_info = None
        try:
            return fn(*args, **kwargs)
        except catch, e:
            body = format_exc()
            exc_info = sys.exc_info()
            logger.exception('exc_mailer() caught an exception, email will be sent')
            try:
                send_mail_func(body)
            except Exception:
                logger.exception('exc_mailer(): send_mail_func() threw an exception, logging it & then re-raising original exception')
                raise exc_info[0], exc_info[1], exc_info[2]
        finally:
            # delete the traceback so we don't have garbage collection issues.
            # see warning at: http://docs.python.org/library/sys.html#sys.exc_info
            if exc_info is not None:
                del exc_info
    return decorate

class Retry(object):
    def __init__(self, tries, exceptions, delay=0.1, logger=None, msg=None):
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
        self.msg = msg

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapfn(*args, **kwargs):
            for _ in xrange(self.tries):
                try:
                    return fn(*args, **kwargs)
                except self.exceptions, e:
                    if self.msg is not None and self.msg not in str(e):
                        raise
                    self.log.debug("Retry, exception: %s", e)
                    time.sleep(self.delay)
            # should only get to this point of we have an
            # exception and have run out of tries
            raise
        return wrapfn
retry = Retry
