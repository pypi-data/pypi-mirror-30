from .redis_cache import RedisCache


class OSCache(RedisCache):

    def __init__(self, redis_host, redis_port,
                 default_timeout):
        super(OSCache, self).__init__(redis_host, redis_port,
                                      default_timeout)

    def put_in_cache(self, package_id, query, path, item):
        params = {'q': query, 'p': path}
        context = package_id
        super(OSCache, self).put(context, params, item)

    def get_from_cache(self, package_id, query, path):
        params = {'q': query, 'p': path}
        context = package_id
        return super(OSCache, self).get(context, params)
