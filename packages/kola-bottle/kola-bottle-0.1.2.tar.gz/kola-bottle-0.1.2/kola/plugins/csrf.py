"""

  `Kola CSRF Plugin`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2014 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
from urllib.parse import unquote
from vital import security

from kola.requests import request
from kola.responses import response, HTTPError
from kola.plugins import Plugin


__all__ = ('Csrf', 'CsrfError')


class Csrf(Plugin):

    def __init__(self, name=None, label="csrf", use_form=None, cookie=None,
                 safe_methods=None, origins=None, token_size=0):
        """ `CSRF Cross-Domain Security Plugin`

            @name: (#str) header or form field name
            @label: (#str) name of the plugin as well as the keyname which
                references options for the plugin within :class:vital.config
            @use_form: (#bool) will use form data rather than headers
                to validate the token if set to |True|
            @cookie: (#dict) :class:SimpleCookie options
            @safe_methods: (#list) list of request methods to always allow
            @origins: (#list) list of origin hostnames to whitelist e.g
                |['yourdomain.com', 'api.yourdomain.com']|
            @token_size: (#int) CSRF token size in bits of entropy,
                default is 128
        """
        self.label = label
        self._name = name
        self._cookie_options = cookie
        self._safe_methods = safe_methods
        self._use_form = use_form
        self._origins = origins
        self._token_size = token_size
        self._config = {}

    def apply(self, route):
        """ Tests to see if the request is CSRF valid. Also sets a response
            cookie if a cookie has yet to be created.
        """
        self._config = route.app.config
        if not self.is_valid:
            raise CsrfError("The CSRF token given was invalid or the origin "
                            "was not allowed.",
                            403)
        if not self.cookie:
            self.set_cookie()
    __call__ = apply

    @property
    def config(self):
        return self._config.get(self.label, {})

    @property
    def name(self):
        if self._name:
            return self._name
        cfg = self.config
        r = cfg.get('request')
        h = cfg.get('header')
        name = 'x-csrf-token'
        if h:
            name = h.get('name', 'name')
        elif r:
            name = r.get('name', name)
            self._use_form = True
        return name

    @property
    def cookie_options(self):
        cfg = self.config
        return self._cookie_options or cfg.get('cookie', {
            "name": "csrf",
            "domain": '.' + self._config.get('hostname'),
            "path": "/",
            "secure": False
        })

    @property
    def use_form(self):
        cfg = self.config
        return self._use_form if self._use_form is not None \
            else cfg.get('request')

    @property
    def safe_methods(self):
        cfg = self.config
        safe_methods = self._safe_methods or \
            cfg.get('safe_methods', ['GET', 'OPTIONS', 'HEAD'])
        return {method.upper() for method in safe_methods}

    @property
    def origins(self):
        cfg = self.config
        default_origin = self.cookie_options['domain'].lstrip('.')
        return set(self._origins or cfg.get('origins', [default_origin]))

    @property
    def token_size(self):
        cfg = self.config
        return self._token_size or cfg.get('token_size', 128)

    @property
    def is_valid(self):
        """ -> #bool |True| if the :prop:token is the same as
                :prop:cookie or the request method is considered CSRF
                safe. Also returns |True| if no CSRF options are specified
                in the configuration.
        """
        if request.method in self.safe_methods:
            return True
        # print(request.cookies, self.token, self.referer_is_valid)
        if self.cookie and self.token and self.referer_is_valid:
            return security.lscmp(self.cookie, self.token)
        return False

    @property
    def token(self):
        """ -> #str CSRF token from the request headers if it is present,
                otherwise tries to find a token within the request body
        """
        if not self.use_form:
            header = request.headers.get(self.name)
            token = unquote(header) if header else header
        else:
            token = unquote(getattr(request, request.method).get(self.name))
        return token

    @property
    def cookie(self):
        """ -> #str CSRF token from the request cookies """
        options = self.cookie_options
        cookie_name = options.get('name', 'csrf')
        cookie = request.get_cookie(cookie_name, secret=options.get('secret'))
        return cookie

    @property
    def referer_is_valid(self):
        """ -> (#bool) True if a referer in :prop:origins made the request """
        return request.http_host == request.referer.netloc or \
            request.referer.netloc in self.origins or '*' in self.origins

    def generate_token(self, size=0):
        """ Generates a random token for CSRF cookies and headers
            @size: (#int) size of token in bits
            -> (#str) random CSRF token
        """
        size = size or self.token_size
        return security.randkey(size)

    def set_cookie(self, **options):
        """ Generates a CSRF token and sets a cookie in the response. """
        cookie_options = options or self.cookie_options.copy()
        cookie_name = cookie_options.get('name', 'csrf')
        if 'name' in cookie_options:
            del cookie_options['name']
        response.set_cookie(cookie_name,
                            self.generate_token(),
                            **cookie_options)


class CsrfError(HTTPError):
    def __init__(self, message, status_code=403):
        self.message = message
        self._status_code = 403
