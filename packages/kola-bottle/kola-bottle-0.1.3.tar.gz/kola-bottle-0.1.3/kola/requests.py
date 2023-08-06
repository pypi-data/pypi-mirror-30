import copy
import pycountry
import babel
from io import BytesIO
from tempfile import TemporaryFile
from cgi import FieldStorage
from http.cookies import SimpleCookie
from collections import namedtuple
from urllib.parse import parse_qsl, quote, urlparse, unquote

from vital import security
from vital.debug import preprX
from vital.cache import DictProperty, local_property
from vital.tools import encoding
from vital.tools.http import parse_auth

from kola.serializers import loads
from kola.wsgi import *


__all__ = ('BaseRequest', 'Request', 'request')


HttpAuth = namedtuple('HttpAuth', 'user password')


class BaseRequest(object):
    """ Storage wrapper for incoming WSGI requests. An instance of this
        is locally bound to :var:request

        Request headers and environment variables are all accessible
        as attributes via this class.
        e.g. |request.http_geoip_city  # -> request.environ["http_geoip_city"]|

        =======================================================================
        ``Usage Example``
        ..
            from kola import request

            print(request.headers)
            # MultiDict({
            #    "header1": ["val1", "val2"]
            # })

            print(request.POST)
            # FormsDict({
            #    "field1": "val"
            # })

            print(request.get_cookie("session_cookie"))
            # FormsDict({
            #   "session_cookie": "cookie_value"
            # })
        ..

        ©2014, Marcel Hellkamp
        ©2015, Refactored by Jared Lunde
    """

    # Maximum size of memory buffer for `body` in bytes.
    MEMFILE_MAX = 10000000  # 10M
    # CGI header keys
    cgikeys = {'CONTENT_TYPE', 'CONTENT_LENGTH'}

    def __init__(self, environ=None):
        """ `Kola Requests`
            @environ: WSGI environ #dict
        """
        self.environ = environ or {}

    __repr__ = preprX('method', 'request_uri', 'remote_addr', keyless=True,
                      address=False)

    def __getattr__(self, name):
        """ Returns an attribute in the local :prop:headers """
        if name == 'environ':
            return self
        else:
            try:
                return self.environ['kola.request.ext.' + name]
            except KeyError:
                return self.headers.get(name)

    def __setattr__(self, name, value):
        """ Sets an attribute in the local :prop:environ """
        if name == 'environ':
            return object.__setattr__(self, name, value)
        self.environ['kola.request.ext.' + name] = value

    def __getitem__(self, key):
        """ -> @key from :prop:environ """
        return self.environ[key]

    def __delitem__(self, key):
        """ Deletes @key from :prop:environ """
        self[key] = ""
        del(self.environ[key])

    def __iter__(self):
        """ -> #iter of :prop:environ """
        return iter(self.environ)

    def __len__(self):
        """ -> #len of :prop:environ """
        return len(self.environ)

    def copy(self):
        """ -> new :class:Request with a shallow :prop:environ copy. """
        return Request(self.environ.copy())

    __copy__ = copy

    def __getstate__(self):
        return self.environ.copy()

    def __setstate__(self, state):
        self.environ = state

    @DictProperty('environ', 'kola.request.headers', read_only=True)
    def headers(self):
        """ Returns the request headers, caches them in the local
            #dict property

            -> :class:WSGIHeaderDict """
        return WSGIHeaderDict(self.environ)

    @property
    def is_jsonp(self):
        """ -> #bool whether or not an x-jsonp-request-method header was sent.
               This header is used for specifying a request method on JSONp
               requests, so as not to break RESTful components.
        """
        return "x_jsonp_request_method" in self.query

    @DictProperty('environ', 'kola.request.method', read_only=True)
    def method(self):
        """ -> Uppercase #str of the :prop:environ REQUEST_METHOD """
        try:
            method = self.query.pop("x_jsonp_request_method")
            return method.upper()
        except KeyError:
            return self.environ.get('REQUEST_METHOD', 'GET').upper()

    def get_auth(self, digest=None):
        """ @digest: hashing function to pass the password through

            -> (#tuple(#str user, #str password)))
        """
        user, pwd = parse_auth(self.headers.get('Authorization', ''))
        if digest is not None:
            pwd = digest(pwd)
        return HttpAuth(user, pwd)

    @DictProperty('environ', 'kola.request.home')
    def home(self):
        return '%s://%s' % (self.environ['wsgi.url_scheme'], self.http_host)

    @DictProperty('environ', 'kola.request.base_url', read_only=True)
    def base_url(self):
        """ -> http(s)://your_hostname.com/your-path """
        return "%s://%s%s" % (self.environ['wsgi.url_scheme'],
                              self.http_host,
                              self.path_info or "")

    @DictProperty('environ', 'kola.request.uri', read_only=True)
    def uri(self):
        """ -> (#str) URI string """
        return self.environ.get("REQUEST_URI",
                                self.environ.get("PATH_INFO", "/"))

    @DictProperty('environ', 'kola.request.query', read_only=True)
    def query(self):
        """ The :prop:query_string parsed into a :class:FormsDict. These
            values are sometimes called "URL arguments" or "GET parameters",
            but not to be confused with "URL wildcards" as they are provided
            by the :class:Router.

            -> :class:FormsDict of the parsed ?query=string
        """
        qs = self.environ.get('QUERY_STRING', '')
        qs = encoding.recode_unicode(unquote(qs))
        return FormsDict(parse_qsl(qs))

    @DictProperty('environ', 'kola.request.post', read_only=True)
    def POST(self):
        """ The values of :prop:forms and :prop:files combined into a single
            :class:FormsDict. Values are either strings (form values) or
            instances of :class:cgi.FieldStorage (file uploads).

            -> :class:FormsDict of the post data received in the request

            ©2014, Marcel Hellkamp
            ©2015, Refactored by Jared Lunde
        """
        # If the request method is JSONP, send back the query data
        if self.is_jsonp:
            data = self.query.copy()
            del data["x_jsonp_request_method"]
            try:
                del data["callback"]
            except KeyError:
                pass
            return data
        # We default to application/x-www-form-urlencoded for everything that
        # is not multipart and take the fast path (also: 3.1 workaround)
        if not self.content_type.startswith('multipart/'):
            if self.json:
                pairs = self.json.items()
            else:
                pairs = map(lambda x: (encoding.recode_unicode(str(x[0])),
                                       encoding.recode_unicode(x[1])),
                            parse_qsl(encoding.uniorbytes(self.body_string)))
            return FormsDict(pairs)
        safe_env = {'QUERY_STRING': ''}  # Build a safe environment for cgi
        for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
            if key in self.environ:
                safe_env[key] = self.environ[key]
        args = dict(fp=self._body, environ=safe_env, keep_blank_values=True,
                    encoding="utf8")
        data = FieldStorage(**args)
        # http://bugs.python.org/issue18394#msg207958
        self.environ['_cgi.FieldStorage'] = data
        data = data.list or []
        post = FormsDict()
        add_post = post.add
        for item in data:
            if item.filename:
                add_post(item.name, FileUpload(item.file,
                                               item.name,
                                               item.filename,
                                               item.headers))
            else:
                add_post(item.name, item.value)
        return post

    GET, get = query, query
    post, put, patch, delete, options, PUT, PATCH, DELETE, OPTIONS = \
        POST, POST, POST, POST, POST, POST, POST, POST, POST

    @DictProperty('environ', 'kola.request.cookies', read_only=True)
    def cookies(self):
        """ -> :class:FormsDict of cookies included in the request """
        return FormsDict((
            (c.key, c.value)
            for c in SimpleCookie(self.headers.get('http_cookie')).values()
        ))

    def cookie(self, name):
        """ -> Cookie from the request as a :class:http.cookies.SimpleCookie
        """
        val = self.cookies.get(name)
        if val is not None:
            return unquote(val)

    def get_cookie(self, name, secret=None):
        """ @name: #str name of the cookie

            -> Cookie from the request as a :class:http.cookies.SimpleCookie,
                optionally decrypts it using @secret """
        try:
            cookie = self.cookie(name) if not secret else \
                security.cookie(self.cookie(name), secret=secret)
        except TypeError:
            return None
        else:
            return cookie

    def get_cookies(self, *names, secret=None):
        """ @names: #str names of the cookies
                e.g. |request.get_cookies("session", "auth")|

            -> (:class:OrderedDict) Cookies from the request as
                :class:http.cookies.SimpleCookie
        """
        names = set(names)
        return OrderedDict([(key, self.get_cookie(key, secret=secret))
                            for key, cookie in self.cookies.items()
                            if not names or key in names])

    @DictProperty('environ', 'kola.request.files', read_only=True)
    def files(self):
        """ -> File uploads parsed from `multipart/form-data` encoded POST or
               PUT request body. The values are instances of
               :class:FileUpload
            ©2014, Marcel Hellkamp
        """
        return FormsDict((name, item)
                         for name, item in self.POST.items()
                         if isinstance(item, FileUpload))

    @property
    def content_length(self):
        """ -> CGI header for CONTENT_LENGTH """
        return int(self.environ['CONTENT_LENGTH'] or -1)

    @property
    def content_type(self):
        """ -> CGI header for CONTENT_TYPE """
        return self.environ['CONTENT_TYPE']

    @property
    def is_xhr(self):
        """ -> #bool true if xmlhttprequest header is set """
        return self.headers.get('http_x_requested_with') and \
            'xmlhttprequest' in \
            self.headers.get('http_x_requested_with').lower()

    @property
    def chunked(self):
        """ -> #bool true if transfer_encoding header is set """
        return self.headers.get('http_transfer_encoding') \
            and 'chunked' in self.headers.get('http_transfer_encoding').lower()

    @DictProperty('environ', 'kola.request.remote_route', read_only=True)
    def remote_route(self):
        """ -> A #list of all IPs that were involved in this request
               Starting with the client IP and followed by zero or more
               proxies. This does only work if all proxies support the
               |X-Forwarded-For| header. Note that this information can be
               forged by malicious clients.

            ©2014, Marcel Hellkamp
        """
        client_ip = self.environ.get('HTTP_X_CLIENT_IP')
        if client_ip:
            return [ip.strip() for ip in client_ip.split(',')]

        proxy = self.environ.get('HTTP_X_FORWARDED_FOR')
        if proxy:
            return [ip.strip() for ip in proxy.split(',')]
            
        remote = self.environ.get('REMOTE_ADDR')
        return [remote] if remote else []

    @property
    def remote_addr(self):
        """ -> The client IP as a #str. Note that this information can be forged
               by malicious clients. """
        route = self.remote_route
        return route[0] if route else None

    @DictProperty('environ', 'kola.request.referer', read_only=True)
    def referer(self):
        return urlparse(self.http_referer)

    @DictProperty('environ', 'kola.request.location', read_only=True)
    def location(self):
        """ -> :class:GeoLocation if 'GeoIP' headers are present """
        return GeoLocation(city=self.geoip_city,
                           postal_code=self.geoip_postal_code,
                           region=self.geoip_region,
                           country=self.geoip_city_country_name,
                           country_code=self.geoip_city_country_code,
                           country_code3=self.geoip_city_country_code3,
                           continent=self.city_continent_code,
                           latitude=self.geoip_latitude,
                           longitude=self.geoip_longitude)

    @DictProperty('environ', 'kola.request.language', read_only=True)
    def language(self):
        lang = self.accept_language
        if lang:
            for opt in lang.split(';'):
                for l in opt.split(','):
                    l, *_ = l.strip().split('-')
                    try:
                        return pycountry.languages.get(iso639_1_code=l)
                    except KeyError:
                        continue
        return pycountry.languages.get(alpha_2='en')

    @DictProperty('environ', 'kola.request.locale', read_only=True)
    def locale(self):
        loc = self.location
        if loc.country_code:
            try:
                return babel.Locale(str(self.language), loc.country_code)
            except babel.core.UnknownLocaleError:
                pass
        lang = self.accept_language
        if lang:
            for opt in lang.split(';'):
                for l in opt.split(','):
                    if '-' in l:
                        try:
                            return babel.Locale.parse(l, sep='-')
                        except babel.core.UnknownLocaleError:
                            pass
                    elif '_' in l:
                        try:
                            return babel.Locale.parse(l)
                        except babel.core.UnknownLocaleError:
                            pass

        return babel.Locale('en', 'US')

    def _iterbody(self, read, bufsize):
        # ©2014, Marcel Hellkamp
        maxread = max(0, int(self.content_length or 0))
        while maxread:
            part = read(min(maxread, bufsize))
            if not part:
                break
            maxread -= len(part)
            yield part

    def _iter_chunked(self, read, bufsize):
        # ©2014, Marcel Hellkamp
        # Refactored by Jared Lunde
        err = HTTPError(400, 'Error while parsing chunked transfer body.')
        rn, sem, bs = b'\r\n', b';', b''
        while True:
            header = read(1)
            while header[-2:] != rn:
                c = read(1)
                header += c
                if not c:
                    raise err
                if len(header) > bufsize:
                    raise err
            size, _, _ = header.partition(sem)
            try:
                maxread = int(encoding.uniorbytes(size.strip()), 16)
            except ValueError:
                raise err
            if maxread == 0:
                break
            buff = bs
            while maxread > 0:
                if not buff:
                    buff = read(min(maxread, bufsize))
                part, buff = buff[:maxread], buff[maxread:]
                if not part:
                    raise err
                yield part
                maxread -= len(part)
            if read(2) != rn:
                raise err

    @DictProperty('environ', 'kola.request.body', read_only=True)
    def _body(self):
        # ©2014, Marcel Hellkamp
        # Refactored by Jared Lunde
        body_iter = self._iter_chunked if self.chunked else self._iterbody
        read_func = self.environ['wsgi.input'].read
        body, body_size, is_temp_file = BytesIO(), 0, False
        l = len
        write_body = body.write
        for part in body_iter(read_func, self.MEMFILE_MAX):
            write_body(part)
            body_size += l(part)
            if not is_temp_file and body_size > self.MEMFILE_MAX:
                body, tmp = TemporaryFile(mode='w+b'), body
                write_body(tmp.getvalue())
                del tmp
                is_temp_file = True
        self.environ['wsgi.input'] = body
        body.seek(0)
        return body

    @DictProperty('environ', 'kola.request.json', read_only=True)
    def json(self):
        """ If the 'Content-Type' header is 'application/json', this
            property holds the parsed content of the request body. Only
            requests smaller than :prop:MEMFILE_MAX are processed to avoid
            memory exhaustion.

            ©2014, Marcel Hellkamp
        """
        if 'application/json' in self.content_type.lower():
            body = encoding.uniorbytes(self.body_string)
            return loads(encoding.recode_unicode(body)) if body else None
        return None

    @DictProperty('environ', 'kola.request.body', read_only=True)
    def body_string(self):
        """ Read body until content-length or MEMFILE_MAX into a string. Raise
            HTTPError(413) on requests that are too large.

            ©2014, Marcel Hellkamp
        """
        clen = int(self.content_length or 0)
        if clen > self.MEMFILE_MAX:
            raise HTTPError(413, 'Request too large')
        if clen < 0:
            clen = self.MEMFILE_MAX + 1
        data = self._body.read(clen)
        if len(data) > self.MEMFILE_MAX:  # Fail fast
            raise HTTPError(413, 'Request too large')
        return data

    @property
    def body(self):
        """ -> The HTTP request body as a seek-able file-like object.
            Depending on :prop:MEMFILE_MAX, this is either a temporary file
            or a :class:io.BytesIO instance. Accessing this property for
            the first time reads and replaces the ``wsgi.input`` environ
            variable. Subsequent accesses just do a `seek(0)` on the file
            object.
        """
        self._body.seek(0)
        return self._body


class Request(BaseRequest):
    """ A locally bound storage wrapper for incoming WSGI requests. """
    bind = BaseRequest.__init__
    environ = local_property()


request = Request()
