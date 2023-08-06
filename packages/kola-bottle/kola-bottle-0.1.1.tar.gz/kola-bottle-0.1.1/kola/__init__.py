"""

  `Kola` a.k.a. Kola Bottle (Kind of Like a Bottle)
   http://github.com/jaredlunde/kola
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--

  A friendly refactor of Bottle.py by Marcel Hellkamp: http://bottlepy.org/

  |[✓]| Built-in Configuration: :attr:kola.Config
  |[✓]| Automatic JSON(p) responses when applicable/turned on
  |[✓]| Built-in Templates w/ Jinja2: :class:kola.View
  |[✓]| Fast, expressive routing: :class:kola.Router
  |[✓]| Plugins: :mod:kola.plugins
  |[✓]| Sessions: :class:kola.plugins.Session
  |[✓]| Caching: :class:kola.plugins.Cache
  |[✓]| Logging and debugging: :func:kola.logg
  |[✓]| Python 3.4+ compatibility

  ..
  from kola import Kola, View, get

  app = Kola()
  app.config['appname'] = 'Kola Bottle'

  @get('/')
  def hello_world():
      return 'Hello world. Welcome to {}.'.format(app.config['appname'])

  @get('/<name([\w\s]+)>')
  def hello(name):
      return 'Hello {}'.format(name)

  @get('/<pong>')
  def ping(pong):
      view = View('pong')
      return view(ping=pong)

  if __name__ == '__main__':
      app.run()
      # WSGIRefServer(host=0.0.0.0, port=8000, )
      # Serving on port 8000:
      # --Request to http://host:8000/--
      # 60.120.123.00 - - [18/Sep/2015 18:47:17] "GET / HTTP/1.1" ...
      #   -> Hello world. Welcome to Kola Bottle.
  ..

--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
  The MIT License (MIT) ©2016 Marcel Hellkamp, Jared Lunde

"""
from functools import wraps
from vital.cache import local_property

from kola.appstack import apps
from kola.conf import Config, config
from kola import plugins
from kola.responses import *
from kola.requests import *
from kola.kola import *
from kola.templates import *
from kola.routing import *
from kola.exceptions import *
from kola.loggers import *
from kola.shortcuts import *
from kola.wsgi import *


__version__ = "0.0.1"
__encoding__ = "utf8"
__license__ = 'MIT'
__author__ = "Marcel Hellkamp, Jared Lunde"


__all__ = (
  "plugins",
  "Config",
  "config",
  "logg",
  "Kola",
  "Schema",
  "BaseRequest",
  "BaseResponse",
  "Request",
  "Response",
  "Router",
  "Route",
  "Template",
  "template",
  "View",
  "url_for",
  "link_for",
  "redirect",
  "abort",
  "static_file",
  "hook",
  "enter",
  "exit",
  "route",
  "get",
  "post",
  "patch",
  "put",
  "options",
  "delete",
  "local",
  "install",
  "uninstall",
  "apps",
  "HTTP_CODES",
  "HTTP_STATUS_LINES",
  "HTTPResponse",
  "HTTPError",
  "request",
  "response",
  "WSGIHeaderDict",
  "FormsDict",
  "HeaderDict",
  "FileUpload",
  "WSGIFileWrapper",
  "GeoLocation",
  "WSGIRefServer"
)


#
#  ``Decorators``
#
def make_default_app_wrapper(name):
    """ Return a callable that relays calls to the current default app.
        ©2014, Marcel Hellkamp
    """
    @wraps(getattr(Kola, name))
    def wrapper(*a, **ka):
        return getattr(apps(), name)(*a, **ka)
    return wrapper


def make_default_route_wrapper(name, **kwargs):
    """ Return a callable that relays calls to the current default app.
        ©2014, Marcel Hellkamp
    """
    @wraps(getattr(Kola, name))
    def wrapper(*a, **ka):
        if callable(a[0]):
            return getattr(apps(), name)("*", callback=a[0])

        @wraps(a, ka)
        def do(obj):
            return getattr(apps(), name)(*a, callback=obj, **ka)
        return do
    return wrapper


# ©2014, Marcel Hellkamp
hook = make_default_app_wrapper('hook')
enter = make_default_app_wrapper('enter')
exit = make_default_app_wrapper('exit')
route = make_default_route_wrapper('route')
get = make_default_route_wrapper('get')
post = make_default_route_wrapper('post')
put = make_default_route_wrapper('put')
patch = make_default_route_wrapper('patch')
options = make_default_route_wrapper('options')
delete = make_default_route_wrapper('delete')
install = make_default_app_wrapper('install')
uninstall = make_default_app_wrapper('uninstall')


#
#  ``Local-thread storage access``
#
local = local_property()
local = {}
