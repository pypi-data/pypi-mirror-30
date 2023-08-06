"""

  `Basic HTTP Authentication Plugin`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2016 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
from vital.debug import preprX

from kola.requests import request
from kola.responses import response, HTTPError
from kola.plugins import Plugin


__all__ = ('AuthBasic',)


class AuthBasic(Plugin):
    """ =================
        ``Usage Example``
        ..
            from kola import Kola
            from kola.plugins import AuthBasic

            check_auth = AuthBasic(lambda u, p: p == 'badwaytodothis')

            cool_app = Kola()
            cool_app.install(check_auth)
        ..
    """
    label = 'auth_basic'

    def __init__(self, check, realm="private", text="Access denied",
                 digest=None):
        """ `HTTP Auth Basic` """
        self.check = check
        self.realm = realm
        self.text = text
        self.digest = digest

    __repr__ = preprX(address=False)

    def apply(self, route):
        user, password = request.get_auth(self.digest) or (None, None)
        if user is None or not self.check(user, password):
            headers = response.headers
            headers.update({'WWW-Authenticate':
                            'Basic realm="%s"' % self.realm})
            raise HTTPError(401, self.text, **headers)
