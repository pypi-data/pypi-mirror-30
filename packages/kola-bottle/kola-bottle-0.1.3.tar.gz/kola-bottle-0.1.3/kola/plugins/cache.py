"""

  `Kola Cache`
   Caching middleware for Kola using :class:redis_structures.RedisCache
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2016 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
from collections import UserDict

from vital.cache.decorators import memoize
from vital.debug import preprX
from vital.tools import getitem_in

from kola.requests import request
from kola.plugins import Plugin

from redis_cache import Cache as RedisCache


__all__ = 'Cache', 'CacheTree', 'CacheError'


_local = {}


class Cache(RedisCache, Plugin):
    """ =======================================================================
        ``Usage Example``
        * Using the |@keep| decorator
        ..
            from kola import Kola, request
            from kola.plugins import cache

            cool_app = Kola()
            cache_middleware = cache.Cache(label="cache", ttl=600,
                                           host='127.0.0.1', port=6380)
            cool_app.install(cache_middleware)

            @get('/user/<username>')
            def users_data(**data):
                @request.cache.keep(300)
                def ud(data):
                    print("UNCACHED")
                    return RestAPI(Users())(data)
                return ud(data)
        ..

        * Using the |@keep| decorator with a nested cache
        ..
            cache_middleware = cache.Cache(label="cache_nest.shard0", ttl=600,
                                           host='127.0.0.1', db=0, port=6380)
            cache_middleware2 = cache.Cache(label="cache_nest.shard1", ttl=600,
                                           host='127.0.0.1', db=1, port=6380)
            cool_app.install(cache_middleware, cache_middleware2)

            @get('/user/<username>')
            def users_data(**data):
                @request.cache_nest.shard1.keep(300)
                def ud(data):
                    print("UNCACHED")
                    return RestAPI(Users())(data)
                return ud(data)
        ..
    """

    def __init__(self, label="cache", name='0', prefix='kola:cache',
                 **kwargs):
        """ `Cache Middleware`

            @label: (#str) key name in Kola :class:kola.config.
                Will also be used as the attribute name which gets
                set in :class:kola.request and the plugin name referenced
                in :class:kola.Route instances. |.| periods in the name
                will create an attribute tree in the :class:kola.request
                starting with the left first. i.e. |'cache.shard1'| creates
                the tree |request.cache.shard1|
            :see::class:redis_cache.Cache

            This plugin is also configurable in the Kola
            :class:kola.config - where the key / value pairs
            get unpacked into :class:RedisCache.

            ..
                "cache": {
                    "name": "1",
                    "prefix":"cool_app:cache:bucket",
                    "ttl": 300,
                    "host": "127.0.0.1",
                    "port": "6379",
                    "password": "Super1337Password",
                    "decode_responses": false
                }
            ..

            This can also be written like:
            ..
                "cache": {
                    "name": "1",
                    "prefix":"cool_app:cache:bucket",
                    "ttl": 300,
                    "use": "redis"
                },
                "redis": {
                    "host": "127.0.0.1",
                    "port": "6379",
                    "password": "Super1337Password",
                    "decode_responses": false
                }
            ..

            The config may be nested and referenced via the label as well.
            e.g. |label='cache.shard0'|
            ..
                "cache": {
                    "shard0": {
                        "name": "1",
                        "prefix":"cool_app:cache:bucket",
                        "ttl": 300,
                        "host": "127.0.0.1",
                        "port": "6379",
                        "password": "Super1337Password",
                        "decode_responses": false
                    }
                }
            ..
            :see::meth:RedisCache.__init__
        """
        super().__init__(prefix=prefix, name=name, **kwargs)
        self.label = label

    __repr__ = preprX('key_prefix', '_ttl', address=False, keyless=True)

    @memoize
    def _get_config(self, route):
        cfg = {'ttl': self._ttl,
               'label': self.label,
               'name': self.name,
               'prefix': self.prefix,
               'serializer': self.serializer,
               'serialize': self.serialized,
               'save_empty': self.save_empty,
               'client': self._client_conn}
        cfg.update(self._client_config)

        try:
            cfg.update(getitem_in(route.app.config, self.label))
        except KeyError:
            pass

        return cfg

    def apply(self, route):
        # cache = Cache(**self._get_config(route))
        cache = _get_cache(**self._get_config(route))
        kn = self.label.split(".")
        tree = request

        if len(kn) == 1:
            setattr(tree, self.label, cache)
        else:
            for n, k in enumerate(kn[:-1], 1):
                attr = getattr(tree, k)
                if attr is not None and not isinstance(attr, CacheTree):
                    raise CacheError("Key `{}` is already used in the "
                                     "request environ and is not a "
                                     "CacheTree().".format(k))
                elif attr and len(attr):
                    tree = attr
                    continue
                else:
                    setattr(tree, k, CacheTree())
            setattr(tree, kn[-1], cache)

    def close(self):
        if self._client_conn is not None:
            try:
                self._client_conn.close()
            except AttributeError:
                pass

    __call__ = apply


@memoize
def _get_cache(**opt):
    return Cache(**opt)


class CacheTree(UserDict):

    def __init__(self, **data):
        self.data = data

    __repr__ = preprX('data')

    def __getattr__(self, name):
        if name == 'data':
            return self.__dict__.get('data', {})
        if name not in self.__dict__:
            try:
                return self.data[name]
            except KeyError:
                return None
        return self.__dict__[name]

    def __setattr__(self, name, value):
        if name == 'data':
            self.__dict__[name] = value
        else:
            self.data[name] = value

    def __delattr__(self, name):
        del self.data[name]

    def __len__(self):
        return len(self.data)


class CacheError(Exception):

    def __init__(self, message):
        self.message = message
