from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable

from config import settings
from connections.redis_manager import RedisManager
from utils import generate_cache_key

cache_instance = RedisManager()


def cached(expiration_seconds: int = settings.DEFAULT_CACHE_EXPIRATION):
    """
    A decorator for caching method results.

    The method name will be used as the cache key prefix.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Use the function's name as the cache key prefix
            cache_key_prefix = func.__name__

            # Generate cache key
            cache_key = generate_cache_key(cache_key_prefix, *args[1:], **kwargs)

            # Check cache
            cached_data = cache_instance.get(cache_key)
            if cached_data:
                return cached_data

            # Call the original function
            if iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Store the result in cache
            cache_instance.set(cache_key, result, ex=expiration_seconds)
            return result

        return wrapper

    return decorator
