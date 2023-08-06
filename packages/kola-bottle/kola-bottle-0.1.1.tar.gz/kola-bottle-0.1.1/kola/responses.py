import datetime
from itertools import chain
from cgi import FieldStorage
from http.cookies import SimpleCookie
from urllib.parse import quote

from vital import security
from vital.debug import preprX, table_mapping
from vital.cache import DictProperty, local_property
from vital.tools import http as http_tools

from kola.wsgi import *


__all__ = ('BaseResponse', 'Response', 'response', 'HTTPResponse', 'HTTPError')


class BaseResponse(object):
    """ Storage wrapper for output WSGI responses. An instance of this
        is locally bound to :var:response

        =======================================================================
        ``Usage Example``
        ..
            from kola import response

            response.set_header("x-kola-hello", "world")
            response.set_cookie("hello", "world")

            response["x-kola-hello"] = "world"  # Sets response header for
                                                # 'x-kola-hello' to 'world'

            response.set_status(404)  # Response returns 404 error
        ..

        ©2014, Marcel Hellkamp
        ©2015, Refactored by Jared Lunde
    """

    # Header blacklist for specific response codes
    # (rfc2616 section 10.2.3 and 10.3.5)
    bad_headers = {
      204: {'Content-Type', 'Content-Length'},
      304: {'Allow', 'Content-Encoding', 'Content-Language',
            'Content-Length', 'Content-Range', 'Content-Type',
            'Content-Md5', 'Last-Modified'}}

    def __init__(self, status=200, body='', content_type='text/html',
                 charset="utf-8", **headers):
        """ `Kola Responses`

            @status: #int response status code
            @body: #str response body content
            @content_type: #str response Content-Type
            @charset: #str reponse charset
            @headers: key=value headers to set for the response
        """
        self._status_code = status
        self._content_type = content_type
        self.body = body
        self._headers = HeaderDict()
        self._cookies = {}
        self.set_content_type(content_type, charset)
        self.set_headers(**headers)

    __repr__ = preprX('method', 'content_type', 'status_line', keyless=True,
                      address=False)

    def __iter__(self):
        """ -> #iter of :prop:body """
        return iter(self.body)

    def __getitem__(self, name):
        """ -> :prop:headers value for @name """
        return self.get_header(name)

    def __setitem__(self, name, value):
        """ Sets the :prop:headers value for @name """
        return self.set_header(name, value)

    def __delitem__(self, name):
        """ Deletes :prop:headers value for @name """
        del self._headers[name]

    def __contains__(self, name):
        """ -> #bool if @name exists in :prop:headers """
        return self.get_header(name)

    def copy(self, cls=None):
        """ -> copy of self """
        cls = cls or BaseResponse
        assert issubclass(cls, BaseResponse)
        copy = cls()
        copy.body = self.body
        copy._status_code = self._status_code
        copy._content_type = self._content_type
        copy._headers = self._headers.copy()
        if self._cookies:
            copy._cookies = SimpleCookie()
            copy._cookies.load(self._cookies.output())
        return copy

    __copy__ = copy

    def __getstate__(self):
        state = {'_status_code': self._status_code,
                 'body': self.body,
                 '_headers': self._headers.copy(),
                 '_content_type': self._content_type}
        if self._cookies:
            state['_cookies'] = SimpleCookie()
            state['_cookies'].load(self._cookies.output())
        return state

    def __setstate__(self, state):
        for attr, val in state.items():
            setattr(self, attr, val)

    @property
    def cookies(self):
        return self._cookies

    def get_cookie(self, name):
        """ -> :class:http.cookies.SimpleCookie for cookie @name """
        val = self._cookies.get(name)
        if val is not None:
            return unquote(val)

    def get_cookies(self, *names):
        """ -> #list of :class:http.cookies.SimpleCookie for cookies @names """
        return [self.get_cookie(name) for name in names]

    def set_cookie(self, name, value, secret=None, **options):
        """ Sets response cookies.
            @name: #str cookie name
            @value: #str cookie value
            @secret: #str secret key to encrypt cookie with
            @options: :class:http.cookies.SimpleCookie options

            ©2015, Marcel Hellkamp
            ©2015, Refactored by Jared Lunde
        """
        if not self._cookies:
            self._cookies = SimpleCookie()
        if not secret:
            self._cookies[name] = quote(str(value), '')
        else:
            self._cookies[name] = security.cookie(value, secret=secret)
        for arg, val in options.items():
            if arg == 'max_age':
                if isinstance(val, datetime.timedelta):
                    val = val.seconds + val.days * 24 * 3600
            if arg == 'expires':
                val = http_tools.http_date(val)
            self._cookies[name][arg.replace("_", "-")] = val

    def set_cookies(self, *dicts):
        """ @dicts: #dict(s) to pass as key=value options
                to :meth:set_cookie """
        for _dict in dicts:
            self.set_cookie(**_dict)

    def delete_cookie(self, name, **options):
        """ Deletes the cookie @name with :class:http.cookies.SimpleCookie
            @options """
        options['max_age'] = -1
        options['expires'] = -1
        self.set_cookie(name, '', **options)

    def delete_cookies(self, *names):
        """ Deletes cookies with @names """
        for name in names:
            self.delete_cookie(name)

    def itercookies(self):
        """ -> #generator of :prop:cookie :class:http.cookies.SimpleCookie
                objects """
        return (cookie for cookie in self.cookies.values())

    @property
    def headers(self):
        """ -> An instance of :class:HeaderDict, a case-insensitive dict-like
                view on the response headers.
        """
        return self._headers

    def add_header(self, name, value):
        """ Adds @value to header @name """
        # response.add_header("x-content-test", "Rods")
        self._headers.add(name, str(value))

    def add_headers(self, name, *values):
        """ Adds multiple @values to header @name """
        # response.add_headers('x_content_test', "Fishing", 'rods')
        for value in values:
            self.add_header(name, value)

    def remove_header(self, name):
        """ Removes header with specified @name
            @name: #str header name
        """
        if key in self._headers:
            del self._headers[key]

    def remove_headers(self, *names):
        """ Removes header with specified @names
            @names: #str header names
        """
        for name in names:
            self.remove_header(name)

    def set_header(self, name, value):
        """ Sets header @name to @value """
        self._headers[name] = str(value)

    def set_headers(self, **headers):
        """ Sets @headers to name=value """
        self._headers.update((k.replace('_', '-'), v)
                             for k, v in headers.items())

    def get_header(self, name, default=None):
        """ Gets @name from :prop:headers
            -> result or @default """
        return self._headers.getone(name, default)

    def get_headers(self, *names, default=None):
        """ Gets @names from :prop:headers
            -> #list of result or @default """
        # response.get_headers("x-content-test", "Content-Type")
        return [self.get_header(k, default) for k in names]

    def iterheaders(self):
        """ -> #iter :prop:headers_list """
        headers = self._headers.items()
        if self._status_code in self.bad_headers:
            headers = filter(
                lambda h: h[0] in self.bad_headers[self._status_code],
                headers)
        return chain(headers,
                     (('Set-Cookie', c.OutputString())
                      for c in self._cookies.values()))

    def listheaders(self):
        """ -> #list of :prop:headers and :prop:cookies """
        return list(self.iterheaders())

    @property
    def content_type(self):
        return self._content_type

    def set_content_type(self, content_type="text/html", charset="utf-8"):
        """ Sets the content type of the response
            @content_type: #str Content-Type
            @charset: #str charset """
        self._content_type = content_type
        self.charset = charset
        content_type = "%s; charset=%s;" % (self._content_type, charset)
        self.set_header('Content-Type', content_type)

    def set_charset(self, charset):
        """ Sets the charset of the response """
        ctype = self.get_header("content-type")
        if ctype and "charset=" in ctype.lower():
            self.content_type = ctype.split("charset=")[0]
        self.set_content_type(self._content_type, charset)

    @property
    def status_line(self):
        """ -> HTTP status line as a string (e.g. ``404 Not Found``). """
        return HTTP_STATUS_LINES[self._status_code]

    @property
    def status_code(self):
        """ -> HTTP status code as an integer (e.g. 404). """
        return self._status_code

    def set_cache_ttl(self, cache_ttl):
        """ Sets the cache control headers to the @cache_ttl specified
            @cache_ttl: #int time to live in browser
        """
        self.remove_header("pragma")
        self.set_header('cache-control', 'public, max-age=%s' % cache_ttl)
        self.set_header('expires', (datetime.datetime.utcnow() +
                                    datetime.timedelta(seconds=cache_ttl)
                                   ).strftime("%a, %d %b %Y %H:%M:%S GMT"))

    def set_status(self, code):
        """ Sets the response status to @code
            @code: #int status code
        """
        self._status_code = code

    def close(self):
        """ Closes the body file object if it is a bytes object """
        if hasattr(self.body, 'close'):
            self.body.close()


class Response(BaseResponse):
    """ A thread-local subclass of :class:BaseResponse with a different
        set of attributes for each thread. There is usually only one global
        instance of this class (:var:response). Its attributes are used
        to build the HTTP response at the end of the request/response cycle.
    """
    bind = BaseResponse.__init__
    _status_code = local_property()
    _cookies = local_property()
    _headers = local_property()
    _content_type = local_property()
    body = local_property()


response = Response()


#
#  ``HTTP Response Wrappers``
#
class HTTPResponse(Response, Exception):
    # ©2014, Marcel Hellkamp
    def __init__(self, status=None, body='', **headers):
        super(Response, self).__init__(status, body, **headers)

    def apply(self, response):
        response._status_code = self._status_code
        response._headers = self._headers
        response._cookies = self._cookies
        response._content_type = self._content_type
        response.body = self.body


class HTTPError(HTTPResponse):
    # ©2014, Marcel Hellkamp
    default_status = 500

    def __init__(self, status=None, body=None, exception=None, traceback=None,
                 **headers):
        self.exception = exception
        self.traceback = traceback
        super().__init__(status, body, **headers)
