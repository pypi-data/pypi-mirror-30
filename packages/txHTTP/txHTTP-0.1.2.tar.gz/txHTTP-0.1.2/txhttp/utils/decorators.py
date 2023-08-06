from functools import wraps

from twisted.web.http import Request


class classonlymethod(classmethod):
    """
    Shamelessly taken from Django's utils decorators
    django.utils.decorators.classonlymethod
    """

    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError("This method is available only on the class, not on instances.")
        return super().__get__(instance, cls)


def json_response(func):
    @wraps(func)
    def deco(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                arg.setHeader(b'Content-Type', b'application/json')
                break
        return func(*args, **kwargs)
    deco.__name__ = func.__name__
    deco.__doc__ = func.__doc__
    return deco
