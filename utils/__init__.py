
from functools import wraps


def safe(m, *args, default=None, **kwargs):
    try:
        return m(*args, **kwargs)
    except:
        return default

def cached(func):
    _cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        hargs = [str(a.__hash__ and hash(a) or id(a)) for a in args]
        hkwargs = [str(hash(k)) + str(v.__hash__ and hash(v) or id(v)) for k, v in kwargs]
        key = f"{hargs}_{hkwargs}"
        if key in _cache:
            return _cache[key]
        
        value = func(*args, **kwargs)
        _cache[key] = value
        return value
    return wrapper
