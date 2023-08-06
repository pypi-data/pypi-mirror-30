"""

  `Kola Sessions`
   Session middleware for Kola
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2016 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
import time
import copy
import argon2
from traceback import format_exc

from redis_cache import StrictRedis

from vital.cache import cached_property, memoize
from vital.debug import logg, preprX
from vital.security import randkey
from vital.tools import getitem_in

from kola.requests import request as _request
from kola.responses import response as _response
from kola.plugins import Cache


__all__ = ('Session',)


@memoize
def _get_client(cfg):
    return StrictRedis(**cfg)


class Session(Cache):
    """ =======================================================================
        ``Usage Example``
        ..
            from kola import Kola, request
            from kola.plugins import Session

            app = Kola()
            session = Session(host='localhost', port=6379)
            app.install(session)

            @get('*')
            def hello(*args, **kwargs):
                request.session['hello'] = 'world'

            @exit
            def goodbye():
                print(request.session['hello'])
                # 'world'
                request.session.save()
         ..
    """
    def __init__(self, request=None, response=None, ttl=300, autosync=False,
                 cookie=None, ignore_methods=None, label="session", name="sid",
                 prefix="kola:session", serializer=None,
                 serialize=True, client=None, decode_responses=True,
                 **redis_config):
        """ `Redis Session`
            @request: (:class:kola.Request)
            @response: (:class:kola.Response)
            @ttl: (#int) number of seconds before session becomes stale
            @serializer: object with a 'loads' and 'dumps' attributes
            @autosync: (#bool) True if the session should be saved right away
                on each change
            @cookie: (#dict) :meth:kola.Response.set_cookie options
            @client: (:class:redis.StrictRedis)
            @ignore_methods: (#list) of methods to ignore starting/closing
                sessions for
            @label: (#str) name of the plugin and the keyname which is sought
                out in the app configuration file when looking for options to
                configure the plugin with. In this case it is also the name
                of the attribute which gets created in the :class:_request
                environment.
            :see::meth:redis_cache.Cache.__init__
        """
        super().__init__(label=label, name=name, prefix=prefix,
                         serializer=serializer, serialize=serialize,
                         client=client, save_empty=False,
                         decode_responses=decode_responses, ttl=ttl,
                         **redis_config)
        self.started = False
        self.data = {}
        self.id = None
        self._token = None
        self.ip = None
        self.request = request or _request
        self.response = response or _response
        self.autosync = autosync
        self._cookie_options = cookie or {}

        if ignore_methods:
            self.ignore_methods = {meth.upper() for meth in ignore_methods}
        else:
            self.ignore_methods = {'OPTIONS', 'HEAD'}
            
        self._read_only = True

    __repr__ = preprX('id', 'started', address=False)

    @cached_property
    def _client(self):
        """ Lazy loads the client connection """
        # client = self._client_conn or StrictRedis(**self._client_config)
        return self._client_conn or _get_client(self._client_config)

    def __getitem__(self, name):
        """ Gets @name from the current session, returns None if no
            key is found as opposed to raising a |KeyError|
        """
        if not self.started:
            # raise SessionError("A session has not been started yet.")
            self.start()
        try:
            return self.data['data'][name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        """ Sets @name to @value in the current session, persists immediately
            if :prop:autosync is set to True
        """
        if not self.started:
            # raise SessionError("A session has not been started yet.")
            self.start()
        self._read_only = False
        self.data['data'][name] = value
        if self.autosync:
            self.save()

    def __delitem__(self, name):
        """ Deletes @key in the current session, persists immediately
            if :prop:autosync is set to True
        """
        if not self.started:
            # raise SessionError("A session has not been started yet.")
            self.start()
        self._read_only = False
        del self.data['data'][name]
        if self.autosync:
            self.save()

    def __contains__(self, name):
        """ -> #bool True if key is in the session else False
            ..
                session["key1"] = "value1"

                "key1" in session
                # -> True

                "key2" in session
                # -> False
            ..
        """
        if not self.started:
            # raise SessionError("A session has not been started yet.")
            self.start()
        return name in self.data['data']

    def __len__(self):
        """ ..
                session["test"] = "value"
                len(session)
                # -> 1
            ..
        """
        if not self.started:
            # raise SessionError("A session has not been started yet.")
            self.start()
        return len(self.data['data'])

    def __str__(self):
        try:
            return str(self.data['data'])
        except KeyError:
            return '{}'

    def items(self):
        return self.data['data'].items()

    def keys(self):
        return self.data['data'].keys()

    __iter__ = keys

    def values(self):
        return self.data['data'].values()

    def update(self, data):
        """ @data: (#dict) items to set in session
            ..
                session.update({"key1": "val1", "key2": "val2"})
                print(session)
                # -> {"key1": "val1", "key2": "val2"}
            ..
        """
        if not self.started:
            # raise SessionError("A session has not been started yet.")
            self.start()
        self._read_only = False
        prev_data = self.data['data'].copy()
        self.data['data'].update(data)
        if self.autosync and cmp(prev_data, self.data['data']) != 0:
            self.save()
        return self.data['data']

    def get(self, key, default=None):
        result = self.__getitem__(key)
        if result is None:
            return default
        return result

    @cached_property
    def cookie_options(self):
        return self._cookie_options or {
            "name": self.name,
            "domain": ".%s" % self.request.http_host,
            "path": "/",
            "secure": False
        }

    @property
    def token(self):
        """ The public session token """
        return self._token or self.cookie

    def start(self):
        """ Starts the session """
        if not self.started:
            try:
                if self.token:
                    self.load()
            except (SessionTokenError, ValueError, IndexError,
                    SessionCookieError):
                pass
            if not self.data:
                self.new()
            self.started = True

    def load(self):
        """ Loads session data from the backend """
        result = None
        try:
            result = super().get(self.token)
        except:
            logg(format_exc()).log()
        if result is not None:
            self.verify(result['id'], self.request.remote_addr)
            self.id = result['id']
            self.ip = self.request.remote_addr
            self.data = result

    def new(self):
        """ Creates a new session """
        self.id = randkey(512)
        self.ip = self.request.remote_addr
        self._token = self._get_token(self.id, self.ip)
        self.data = {
            'id': self.id,
            'ip': self.request.remote_addr,
            'created_at': time.perf_counter(),
            'location': (self.request.location.latitude,
                         self.request.location.longitude),
            'data': {}
        }
        self.set_cookie()

    def save(self):
        """ Syncs the local session to the remote backend """
        if self.request.method not in self.ignore_methods and \
           self.started and self.data.get('data') and not self._read_only:
            self._read_only = True
            return self.setex(self.token, self.data)

    HASH_MEMORY_COST, HASH_TIME_COST, HASH_PARALLELISM = 1 << 4, 1, 1

    def _get_token(self, id, ip, size=24):
        string = "%s:%s" % (id, ip)
        hash = argon2.low_level.hash_secret(
            string.encode(),
            randkey(96).encode(),
            time_cost=self.HASH_TIME_COST,
            memory_cost=self.HASH_MEMORY_COST,
            parallelism=self.HASH_PARALLELISM,
            hash_len=size,
            type=argon2.low_level.Type.I,
            version=argon2.low_level.ARGON2_VERSION)
        return "$".join(hash.decode('utf-8').split("$")[-2:])

    def verify(self, id, ip):
        """ Verifies that this is the proper owner of the session via IP
            comparison, helps to prevent cookie theft
        """
        try:
            string = ("%s:%s" % (id, ip)).encode('utf-8')
            hashargs = '$argon2i$m=%s,t=%s,p=%s$' % (self.HASH_MEMORY_COST,
                                                     self.HASH_TIME_COST,
                                                     self.HASH_PARALLELISM)
            hash = (hashargs + self.token).encode('utf-8')
            return argon2.low_level.verify_secret(hash,
                                                  string,
                                                  type=argon2.low_level.Type.I)
        except argon2.exceptions.VerificationError:
            self.invalidate()
            raise SessionTokenError("The initialization ip address did not "
                                    "match the session ip address")

    def clear(self):
        """ Clears the current session data """
        self.data = {}
        self._read_only = False

    def invalidate(self):
        """ Invalidates/removes the current session """
        self.delete_cookie()
        self.remove(self.token)
    destroy = invalidate

    @cached_property
    def cookie(self):
        """ Gets the session cookie if there is one """
        try:
            self._token = self.request.get_cookie(
                self.cookie_options.get('name', self.name),
                secret=self.cookie_options.get('secret')) or ""
            return self._token
        except Exception:
            raise SessionCookieError("No cookie was found.")

    def delete_cookie(self):
        """ Deletes the session cookie """
        settings = self.cookie_options.copy()
        if settings.get('expires'):
            del settings['expires']
        if settings.get('name'):
            del settings['name']
        self.response.delete_cookie(self.cookie_options.get('name', self.name),
                                    **settings)

    def set_cookie(self):
        """ Sets the session cookie """
        settings = self.cookie_options.copy()
        if settings.get('name'):
            del settings['name']
        if settings.get('httponly') is None:
            settings['httponly'] = True
        self.response.set_cookie(self.cookie_options.get('name', self.name),
                                 str(self.token),
                                 **settings)

    @property
    def ttl(self):
        """ Returns the TTL of the current session in seconds """
        return super().ttl(self.token)

    @property
    def pttl(self):
        """ Returns the TTL of the current session in milliseconds """
        return super().pttl(self.token)

    def flush(self):
        """ !! Flushes all session remote keys !! """
        super().flush()
        try:
            self.data['data'].clear()
        except KeyError:
            pass

    def copy(self):
        _cls = copy.copy(self)
        return _cls

    def apply(self, route):
        self.route = route
        if self.request.method not in self.ignore_methods:
            cfg = {'request': self.request,
                   'response': self.response,
                   'ttl': self._ttl,
                   'autosync': self.autosync,
                   'cookie': self._cookie_options,
                   'ignore_methods': self.ignore_methods,
                   'label': self.label,
                   'name': self.name,
                   'prefix': self.prefix,
                   'serializer': self.serializer,
                   'serialize': self.serialized,
                   'client': self._client_conn}
            try:
                cfg.update(getitem_in(route.app.config, self.label))
            except KeyError:
                pass
            setattr(self.request, self.label, self.__class__(**cfg))

    __call__ = apply


class SessionError(BaseException):
    pass


class SessionCookieError(BaseException):
    pass


class SessionTokenError(BaseException):
    pass
