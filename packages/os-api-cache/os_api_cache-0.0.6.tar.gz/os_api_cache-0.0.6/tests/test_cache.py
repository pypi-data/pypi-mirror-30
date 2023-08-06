# -*- coding: utf-8 -*-
import time

import pytest

from redis import StrictRedis

from os_api_cache import OSCache

TIMEOUT = 5


@pytest.fixture
def redis_cache():
    redis_host = 'localhost'
    redis_port = 6379
    redis_connection = StrictRedis(host=redis_host, port=redis_port, db=1)
    redis_connection.flushdb()
    _cache = OSCache(redis_host, redis_port, TIMEOUT)
    return _cache


class TestCache(object):

    def test_ok(self, redis_cache):
        print("OK")

    def test_simple_store(self, redis_cache):
        context = 'context'
        params = {'key': 'value'}
        item = {'a', 'b', 'c'}
        redis_cache.put(context, params, item)
        assert 'a' in redis_cache.get(context, params)

    def test_get_nonexistent(self, redis_cache):
        context = 'context'
        params = {'key': 'value'}
        params2 = {'key': 'value2'}
        item = {'a', 'b', 'c'}
        redis_cache.put(context, params, item)
        assert 'a' in redis_cache.get(context, params)
        assert redis_cache.get(context, params2) is None

    def test_default_timeout(self, redis_cache):
        context = 'context'
        params = {'key': 'value'}
        item = {'a', 'b', 'c'}
        redis_cache.put(context, params, item)
        assert 'a' in redis_cache.get(context, params)
        time.sleep(TIMEOUT)
        assert redis_cache.get(context, params) is None

    def test_nondefault_timeout(self, redis_cache):
        context = 'context'
        params = {'key': 'value'}
        item = {'a', 'b', 'c'}
        redis_cache.put(context, params, item, timeout=TIMEOUT*2)
        time.sleep(TIMEOUT*2-1)
        assert 'a' in redis_cache.get(context, params)
        time.sleep(TIMEOUT)
        assert redis_cache.get(context, params) is None

    def test_nondefault_timeout_reset(self, redis_cache):
        '''key resets timeout to default_timeout after first access.'''
        context = 'context'
        params = {'key': 'value'}
        item = {'a', 'b', 'c'}
        redis_cache.put(context, params, item, timeout=TIMEOUT*2)
        time.sleep(TIMEOUT)
        assert 'a' in redis_cache.get(context, params)
        time.sleep(TIMEOUT)
        assert redis_cache.get(context, params) is None

    def test_clear(self, redis_cache):
        context = 'context'
        params = {'key': 'value'}
        item = {'a', 'b', 'c'}
        redis_cache.put(context, params, item)
        assert 'a' in redis_cache.get(context, params)
        redis_cache.clear(context+'2')
        assert 'a' in redis_cache.get(context, params)
        redis_cache.clear(context)
        assert redis_cache.get(context, params) is None
