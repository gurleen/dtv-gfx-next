import functools


producer_funcs = []


def producer(*args, **kwargs):
    debug_only = kwargs.get("debug_only", False)
    prod_only = kwargs.get("prod_only", False)

    def factory(func):
        producer_funcs.append((func, debug_only, prod_only))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    if len(args) > 0 and callable(args[0]):
        return factory(args[0])
    return factory


def collect_producers():
    return producer_funcs
