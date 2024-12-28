from hashlib import md5
from django.core.cache import cache


def _cache_get_key(*args, **kwargs):
    serialise = [str(arg) for arg in args]
    serialise.extend([f"{key} {arg}" for key, arg in kwargs.items()])

    full_str = " ".join(serialise).encode('utf-8')
    key = md5(full_str).hexdigest()
    return key


def function_cache(*args, **kwargs):
    """
    This is a decorator that caches the result of a function for a specified time.
    """
    time = kwargs.get('time', 60)
    cache_key = kwargs.get('cache_key', None)
    omit_first_arg = kwargs.pop('_omit_first_arg', False)

    if not cache_key:
        cache_key = None

    def decorator(fn):
        def wrapper(*call_args, **call_kwargs):
            _cache_key = cache_key
            if not _cache_key:
                key_call_args = [arg for arg in call_args[1:]] if omit_first_arg else call_args
                _cache_key = _cache_get_key(fn.__module__, fn.__name__, *key_call_args, **call_kwargs)
            result = cache.get(_cache_key)

            if result is None:
                result = fn(*call_args, **call_kwargs)
                cache.set(_cache_key, result, time)
            return result
        return wrapper

    if len(args) == 1 and callable(args[0]) and not kwargs:
        return decorator(args[0])
    return decorator


def method_cache(*args, **kwargs):
    """
    This is a decorator that caches the result of a method for a specified time. It is used for class methods where the
    first argument is a class instance
    """
    kwargs['_omit_first_arg'] = True
    return function_cache(*args, **kwargs)
