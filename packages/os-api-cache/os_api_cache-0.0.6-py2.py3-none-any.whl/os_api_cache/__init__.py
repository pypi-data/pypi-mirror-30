import os
import logging

from .os_cache import OSCache

_the_cache = None


def get_os_cache():
    global _the_cache
    if _the_cache is None and 'OS_API_CACHE' in os.environ:
        host = os.environ.get('OS_API_CACHE')
        cache_timeout = int(os.environ.get('OS_API_CACHE_TIMEOUT', 86400))
        _the_cache = OSCache(host, 6379, cache_timeout)

        logging.info('CACHE %s', _the_cache)
        logging.info('CACHE TIMEOUT %s', cache_timeout)
    return _the_cache
