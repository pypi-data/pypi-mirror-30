"""

  `Kola WSGI Data Structures`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   The MIT License (MIT) © 2015 Marcel Hellkamp, Jared Lunde
   http://github.com/jaredlunde

"""
import re
import os

from http.client import responses as HTTP_CODES
from unicodedata import normalize

import socket
from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
from wsgiref.handlers import CGIHandler

from vital.cache import cached_property
from vital.tools import encoding
from vital.debug import preprX

from kola.multidict import CIMultiDict, MultiDict, _Pair


__all__ = (
  "WSGIHeaderDict",
  "HeaderDict",
  "HeaderProperty",
  "FormsDict",
  "FileUpload",
  "WSGIFileWrapper",
  "GeoLocation",
  "ServerAdapter",
  "CGIServer",
  "WSGIRefServer",
  "HTTP_CODES",
  "HTTP_STATUS_LINES"
)


#
#  ``Headers``
#
class WSGIHeaderDict(CIMultiDict):
    """ This dict-like class wraps a WSGI environ dict and provides
        convenient access to HTTP_* fields. Keys and values are native strings
        (2.x bytes or 3.x unicode) and keys are case-insensitive. If the WSGI
        environment contains non-native string values, these are de- or encoded
        using a lossless 'latin1' character set.
    """
    def __init__(self, environ):
        pair = _Pair
        super().__init__(
            map(lambda k: (self._map(k[0]), k[1]), environ.items()))

    def __getitem__(self, key):
        try:
            return encoding.uniorbytes(self.getone(key))
        except:
            try:
                return self.getone(key)
            except:
                return self._getone(key)

    def __setitem__(self, key, value):
        raise TypeError("{} is read-only.".format(self.__class__))

    def __delitem__(self, key):
        raise TypeError("{} is read-only.".format(self.__class__))

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def items(self):
        for k in self.keys():
            yield (k, self[k])

    def values(self):
        for k in self.keys():
            yield self[k]

    def _map(self, key):
        if key[:4] in {'http', 'Http', 'HTTP'}:
            return key.replace('-', '_')
        return 'http_' + key.replace("-", "_")

    def getone(self, key, default=None):
        return CIMultiDict.getone(self, self._map(key), default)

    def raw(self, key, default=None):
        """ Return the header value as is (may be bytes or unicode). """
        return self.getone(key) or default

    def getall(self, key):
        return CIMultiDict.getall(self, self._map(key))

    def getlist(self, key):
        return self.getall(key)


class HeaderDict(CIMultiDict):
    """ A case-insensitive version of :class:MultiDict that defaults to
        replace the old value instead of appending it. """

    def filter(self, names):
        for name in names:
            if name in self.data:
                del self.data[name]

    def getlist(self, key):
        return self.getall(key)


class HeaderProperty(object):
    # ©2014, Marcel Hellkamp
    def __init__(self, name, reader=None, writer=str, default=''):
        self.name, self.default = name, default
        self.reader, self.writer = reader, writer
        self.__doc__ = 'Current value of the %r header.' % name.title()

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.headers.get(self.name, self.default)
        return self.reader(value) if self.reader else value

    def __set__(self, obj, value):
        obj.headers[self.name] = self.writer(value)

    def __delete__(self, obj):
        del obj.headers[self.name]


#
#  ``Forms``
#
class FormsDict(MultiDict):
    """ This :class:MultiDict subclass is used to store request form data.
        Additionally to the normal dict-like item access methods (which return
        unmodified data as native strings), this container also supports
        attribute-like access to its values. Attributes are automatically de-
        or recoded to match :prop:input_encoding (default: 'utf8'). Missing
        attributes default to an empty string.
        ©2014, Marcel Hellkamp
    """

    #: Encoding used for attribute values.
    input_encoding = 'utf8'
    #: If true (default), unicode strings are first encoded with `latin1`
    #: and then decoded to match :prop:input_encoding.
    recode_unicode = True

    def _fix(self, s, encoding=None):
        if isinstance(s, str) and self.recode_unicode:  # Python 3 WSGI
            return encoding.recode_unicode(s)

    def decode(self, encoding=None):
        """ Returns a copy with all keys and values de- or recoded to match
            :prop:input_encoding. Some libraries (e.g. WTForms) want a
            unicode dictionary. """
        copy = FormsDict()
        enc = copy.input_encoding = encoding or self.input_encoding
        copy.recode_unicode = False
        add_copy = copy.add
        for key, value in self.items():
            add_copy(self._fix(key, enc), self._fix(value, enc))
        return copy

    def getunicode(self, name, default=None, encoding=None):
        """ Return the value as a unicode string, or the default. """
        try:
            return self._fix(self[name], encoding)
        except (UnicodeError, KeyError):
            return default

    def __getattr__(self, name, default=str()):
        # Without this guard, pickle generates a cryptic TypeError:
        if name[:2] == '__' and name[-2:] == '__':
            return super(FormsDict, self).__getattr__(name)
        return self.getunicode(name, default=default)

    def getlist(self, key):
        return self.getall(key)


#
#  ``File Uploads``
#
class FileUpload(object):
    """ Thin wrapper for file uploads containing the file form field name,
        the filename, the file body and any headers. """
    def __init__(self, fileobj, name, filename, headers=None):
        """ @fileobj: bytes object containing file
            @name: name of the form field containing the file
            @filename: raw filename as sent by the client
                (may contain unsafe characters)
            @headers: additional headers sent with the file
        """
        #: Open file(-like) object (BytesIO buffer or temporary file)
        self.file = fileobj
        #: Name of the upload form field
        self.name = name
        #: Raw filename as sent by the client (may contain unsafe characters)
        self.raw_filename = filename
        #: A :class:HeaderDict with additional headers (e.g. content-type)
        self.headers = HeaderDict(headers) if headers else HeaderDict()

    __repr__ = preprX('name', 'raw_filename', 'content_length', 'content_type',
                      address=False)

    content_type = HeaderProperty('Content-Type')
    content_length = HeaderProperty('Content-Length', reader=int, default=-1)

    @cached_property
    def filename(self):
        """ Name of the file on the client file system, but normalized to
            ensure file system compatibility. An empty filename is returned as
            'empty'. Only ASCII letters, digits, dashes, underscores and dots
            are allowed in the final filename. Accents are removed, if
            possible. Whitespace is replaced by a single dash. Leading or
            tailing dots or dashes are removed. The filename is limited to
            255 characters.
        """
        fname = self.raw_filename
        if not isinstance(fname, str):
            fname = fname.decode('utf8', 'ignore')
        fname = normalize('NFKD', fname).encode('ASCII', 'ignore')\
            .decode('ASCII')
        fname = os.path.basename(fname.replace('\\', os.path.sep))
        fname = re.sub(r'[^a-zA-Z0-9-_.\s]', '', fname).strip()
        fname = re.sub(r'[-\s]+', '-', fname).strip('.-')
        return fname[:255] or 'empty'

    def _copy_file(self, fp, chunk_size=2**16):
        read, write, offset = self.file.read, fp.write, self.file.tell()
        while 1:
            buf = read(chunk_size)
            if not buf:
                break
            write(buf)
        self.file.seek(offset)

    def save(self, destination, overwrite=False, chunk_size=2**16):
        """ Save file to disk or copy its content to an open file(-like) object.
            If *destination* is a directory, :prop:filename is added to the
            path. Existing files are not overwritten by default (IOError).
            @destination: #str file path, directory or #bytes file(-like) object
            @overwrite: #bool if True, replace existing files. (default: False)
            @chunk_size: #int bytes to read at a time. (default: 64kb)
        """
        if isinstance(destination, str):  # Except file-likes here
            if os.path.isdir(destination):
                destination = os.path.join(destination, self.filename)
            if not overwrite and os.path.exists(destination):
                raise IOError('File exists.')
            with open(destination, 'wb') as fp:
                self._copy_file(fp, chunk_size)
        else:
            self._copy_file(destination, chunk_size)


class WSGIFileWrapper(object):
    """ Wrapped around the response returned to WSGI if the response
        is file-like. """
    # ©2014, Marcel Hellkamp
    def __init__(self, fp, buffer_size=1024*64):
        """ @fp: file object
            @buffer_size: buffer size to read with
        """
        self.fp, self.buffer_size = fp, buffer_size
        for attr in ('fileno', 'close', 'read', 'readlines',
                     'tell', 'seek'):
            if hasattr(fp, attr):
                setattr(self, attr, getattr(fp, attr))

    def __iter__(self):
        """ Reads the file """
        buff, read = self.buffer_size, self.read
        while True:
            part = read(buff)
            if not part: return
            yield part


#
#  ``GeoIP``
#
class GeoLocation(object):
    """ A GeoIP wrapper providing easy access to any GeoIP information sent in
        the request headers.
    """
    __slots__ = ("city", "postal_code", "region", "country",
                 "country_code", "country_code3", "continent",
                 "latitude", "longitude", )

    def __init__(self, city=None, postal_code=None, region=None, country=None,
                 country_code=None, country_code3=None, continent=None,
                 latitude=None, longitude=None):
        """ Formats and stores GEOIP location data """
        self.city = city
        self.postal_code = postal_code
        self.region = region
        self.country = country
        self.country_code = country_code
        self.country_code3 = country_code3
        self.continent = continent
        self.latitude = latitude
        self.longitude = longitude

    __repr__ = preprX('postal', address=False)

    @property
    def full(self):
        return ", ".join(filter(lambda x: x, (
            self.city, self.region, self.country_code3, self.postal_code,
            self.latitude, self.longitude)))

    @property
    def postal(self):
        return "{}, {} {}\n{}".format(
            self.city, self.region, self.postal_code, self.country)

    @property
    def coord(self):
        return (self.latitude, self.longitude)

    def __str__(self):
        return "{}, {}, {}".format(self.city, self.region, self.country_code3)


class ServerAdapter(object):
    # ©2014, Marcel Hellkamp
    quiet = False

    def __init__(self, host='0.0.0.0', port=8080, **options):
        """ @host: #str local hostname to listen on
            @port: #int local port to listen on
            @**options: passed to the WSGI server
        """
        self.options = options
        self.host = host
        self.port = int(port)

    def run(self, handler):  # pragma: no cover
        pass

    def __repr__(self):
        args = ['host={}'.format(self.host), 'port={}'.format(self.port)]
        args.extend(
            '{}={}'.format(k, repr(v))
            for k, v in self.options.items()
        )
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join(args).rstrip(", "))


class CGIServer(ServerAdapter):
    # ©2014, Marcel Hellkamp
    quiet = True

    def run(self, handler):
        def fixed_environ(environ, start_response):
            environ.setdefault('PATH_INFO', '')
            return handler(environ, start_response)

        CGIHandler().run(fixed_environ)


class WSGIRefServer(ServerAdapter):
    """ ..
            from kola import Kola, get
            from kola import wsgi

            app = Kola(name="Kola Bottle")

            @get('/')
            def hello_world():
                return 'Hello world. Welcome to {}.'.format(app.name)
            if __name__ == '__main__':
                httpd = wsgi.WSGIRefServer(port=8000)
                print(httpd)
                print("Serving on port 8000:")
                # WSGIRefServer(host=0.0.0.0, port=8000, )
                # Serving on port 8000:
                httpd.run(app)
                # --Request to http://host:8000/--
                # 60.120.123.00 - - [18/Sep/2015 18:47:17] "GET / HTTP/1.1" ...
                #   -> Hello world. Welcome to Kola Bottle.
        ..
        ©2014, Marcel Hellkamp
    """
    def __init__(self, *args, quiet=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.quiet = quiet

    def run(self, app):
        """ Runs the WSGI server using func:wsgiref.simple_server.make_server
            @app: your :class:kola.Kola app or wsgi callable
        """
        class FixedHandler(WSGIRequestHandler):

            def address_string(self):  # Prevent reverse DNS lookups please.
                return self.client_address[0]

            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls = self.options.get('server_class', WSGIServer)
        if ':' in self.host:
            # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        self.srv = make_server(
            self.host, self.port, app, server_cls, handler_cls)
        # update port actual port (0 means random)
        self.port = self.srv.server_port
        try:
            self.srv.serve_forever()
        except KeyboardInterrupt:
            self.srv.server_close()  # Prevent ResourceWarning: unclosed socket
            raise


#: A dict to map HTTP status codes (e.g. 404) to phrases (e.g. 'Not Found')
HTTP_CODES[428] = "Precondition Required"
HTTP_CODES[429] = "Too Many Requests"
HTTP_CODES[431] = "Request Header Fields Too Large"
HTTP_CODES[451] = "Unavailable For Legal Reasons "
HTTP_CODES[511] = "Network Authentication Required"
HTTP_STATUS_LINES = {k: '{} {}'.format(k, v) for (k, v) in HTTP_CODES.items()}
