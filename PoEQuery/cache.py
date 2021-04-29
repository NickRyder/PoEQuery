import diskcache  # type: ignore
import time
from PoEQuery import __diskcache_path__
import os
import logging
import inspect
from functools import lru_cache

DEFAULT_EXPIRE = 60 * 60 * 24 * 7 * 2
EXPIRE_ON_LOAD = True


@lru_cache(maxsize=None)
def _lazy_load_cache(directory):
    """
    because decorators are called on module load, we lazy init
    the cache (and potentially .expire() it) so that we don't
    load all the caches from all end points into memory at once
    """
    cache = diskcache.Cache(directory=directory)
    if EXPIRE_ON_LOAD:
        tic = time.monotonic()
        expired_count = cache.expire()
        logging.warn(
            f"Flushed {expired_count} expired entries on load, took {time.monotonic() - tic:0.2f}s"
        )
    return cache


def cache_results(subdirectory, key, expire=DEFAULT_EXPIRE):
    """
    Important: diskcache does NOT use python `hash`, and instead
    will compare based on `pkl.dumps(key)`
    """
    directory = os.path.join(__diskcache_path__, subdirectory)

    def cache_results_decorator(async_fn):

        if inspect.iscoroutinefunction(async_fn):

            async def async_cached_fn(
                *args,
                use_cached=True,
                **kwargs,
            ):
                cache = _lazy_load_cache(directory)
                _key = key(*args, **kwargs)
                if _key in cache and use_cached:
                    cached_result, expire_time = cache.get(_key, expire_time=True)
                    return cached_result
                else:
                    result = await async_fn(*args, **kwargs)
                    cache.set(_key, result, expire=expire)
                    return result

            return async_cached_fn
        else:

            def cached_fn(
                *args,
                use_cached=True,
                **kwargs,
            ):
                cache = _lazy_load_cache(directory)
                _key = key(*args, **kwargs)
                if _key in cache and use_cached:
                    cached_result, expire_time = cache.get(_key, expire_time=True)
                    return cached_result
                else:
                    result = async_fn(*args, **kwargs)
                    cache.set(_key, result, expire=expire)
                    return result

            return cached_fn

    return cache_results_decorator
