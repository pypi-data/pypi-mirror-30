from .task import FunctionTask


def task(name=None):
    def decorator(func):
        if name is None:
            tname = '{}.{}'.format(func.__module__, func.__name__)
        else:
            tname = name
        ftask = FunctionTask(tname, func)
        func.t = ftask
        return func
    if callable(name):
        func = name
        name = None
        return decorator(func)
    else:
        return decorator
