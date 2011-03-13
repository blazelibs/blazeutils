from functools import update_wrapper
import inspect, itertools

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