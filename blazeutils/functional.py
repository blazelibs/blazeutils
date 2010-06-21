import inspect

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
