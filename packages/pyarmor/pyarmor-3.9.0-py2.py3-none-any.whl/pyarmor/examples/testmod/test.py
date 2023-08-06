def wraparmor(func):
    func.__refcalls__ = 0
    def wrapper(*args, **kwargs):
         __wraparmor__(func)
         try:
             return func(*args, **kwargs)
         except Exception as err:
             raise err
         finally:
             __wraparmor__(func, 1)
    wrapper.__module__ = func.__module__
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__.update(func.__dict__)
    # Only for test
    wrapper.orig_func = func
    return wrapper

