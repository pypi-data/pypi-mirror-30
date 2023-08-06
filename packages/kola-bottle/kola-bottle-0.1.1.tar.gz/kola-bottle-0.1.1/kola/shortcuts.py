import os
import time
import mimetypes

from vital.tools.http import parse_date, parse_range_header, parse_auth

from kola.exceptions import *
from kola.wsgi import *
from kola.requests import request
from kola.responses import *


__all__ = ('abort', 'redirect', 'static_file', 'auth_basic')


def abort(code=500, text='Unknown Error.'):
    """ Aborts execution and causes a HTTP error.

        @code: (#int) the status code to redirect with (e.g. 301 if permanent)
        @text: (#str) the description of the error being raised
    """
    raise HTTPError(code, text)


def auth_basic(check, realm="private", text="Access denied", digest=None):
    """ Decorator to require HTTP auth (basic).
        Copyright (c) Marcel Hellkamp
    """
    def decorator(func):
        def wrapper(*a, **ka):
            user, password = request.get_auth(digest) or (None, None)
            if user is None or not check(user, password):
                response.headers['WWW-Authenticate'] = 'Basic realm="%s"' %\
                                                       realm
                return HTTPError(401, text)
            return func(*a, **ka)
        return wrapper
    return decorator


def redirect(url, code=None):
    """ Aborts execution and causes a 303 or 302 redirect, depending on
        the HTTP protocol version.

        @url: (#str) url to redirect to
        @code: (#int) the status code to redirect with (e.g. 301 if permanent)
        Copyright (c) Marcel Hellkamp
    """
    if not code:
        code = 303 if request['SERVER_PROTOCOL'] == "HTTP/1.1" else 302
    response.set_status(code)
    response.body = ""
    response.set_header('Location', url)
    raise HTTPRedirect()


def static_file(filename, root, mimetype='auto', download=False,
                charset='UTF-8'):
    """ Open a file in a safe way and return :exc:`HTTPResponse` with status
        code 200, 305, 403 or 404. The |Content-Type|, |Content-Encoding|,
        |Content-Length| and |Last-Modified| headers are set if possible.
        Special support for |If-Modified-Since|, |Range| and |HEAD|
        requests.
        @filename: Name or path of the file to send.
        @root: Root path for file lookups. Should be an absolute directory
            path.
        @mimetype: Defines the content-type header (default: guess from
            file extension)
        @download: If True, ask the browser to open a `Save as...` dialog
            instead of opening the file with the associated program. You can
            specify a custom filename as a string. If not specified, the
            original filename is used (default: False).
        @charset: The charset to use for files with a ``text/*``
            mime-type. (default: UTF-8)

        Copyright (c) Marcel Hellkamp
    """

    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
    headers = dict()

    if not filename.startswith(root):
        return HTTPError(403, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        return HTTPError(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        return HTTPError(403, "You do not have permission to access this "
                              "file.")

    if mimetype == 'auto':
        if download and download is not True:
            mimetype, encoding = mimetypes.guess_type(download)
        else:
            mimetype, encoding = mimetypes.guess_type(filename)
        if encoding:
            headers['Content-Encoding'] = encoding

    if mimetype:
        if (mimetype[:5] == 'text/' or mimetype == 'application/javascript') \
           and charset and 'charset' not in mimetype:
            mimetype += '; charset=%s' % charset
        headers['Content-Type'] = mimetype

    if download:
        download = os.path.basename(filename if download is True else download)
        headers['Content-Disposition'] = 'attachment; filename="%s"' % download

    stats = os.stat(filename)
    headers['Content-Length'] = clen = stats.st_size
    lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                       time.gmtime(stats.st_mtime))
    headers['Last-Modified'] = lm

    ims = request.environ.get('HTTP_IF_MODIFIED_SINCE')
    if ims:
        ims = parse_date(ims.split(";")[0].strip())
    if ims is not None and ims >= int(stats.st_mtime):
        headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                                        time.gmtime())
        return HTTPResponse(status=304, **headers)

    body = '' if request.method == 'HEAD' else open(filename, 'rb')

    headers["Accept-Ranges"] = "bytes"
    ranges = request.environ.get('HTTP_RANGE')

    def _file_iter_range(fp, offset, bytes, maxread=1024 * 1024):
        fp.seek(offset)
        while bytes > 0:
            part = fp.read(min(bytes, maxread))
            if not part:
                break
            bytes -= len(part)
            yield part
    if 'HTTP_RANGE' in request.environ:
        ranges = list(parse_range_header(request.environ['HTTP_RANGE'], clen))
        if not ranges:
            return HTTPError(416, "Requested Range Not Satisfiable")
        offset, end = ranges[0]
        headers["Content-Range"] = "bytes %d-%d/%d" % (offset, end - 1, clen)
        headers["Content-Length"] = str(end - offset)
        if body:
            body = _file_iter_range(body, offset, end - offset)
        return HTTPResponse(body, status=206, **headers)
    return HTTPResponse(body, **headers)
