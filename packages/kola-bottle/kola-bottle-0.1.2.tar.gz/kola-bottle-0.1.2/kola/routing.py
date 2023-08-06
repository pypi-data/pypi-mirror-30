import re
import string

try:
    from cnamedtuple import namedtuple
except ImportError:
    from collections import namedtuple

from collections import defaultdict

from urllib.parse import unquote
from functools import lru_cache

from vital.debug import preprX
from vital.cache import DictProperty, memoize
from vital.tools import strings as string_tools, import_from
from vital.tools.lists import pairwise

from kola.responses import HTTPError


__all__ = ('Router', 'Route')


class _re_cache(object):
    """ Local compiled regex cache """
    __slots__ = ("_re",)

    def __init__(self):
        self._re = dict()

    def get(self, rule):
        if not self._re.get(rule):
            self._re[rule] = re.compile(rule)
        return self._re[rule]


class RouteParser(string.Formatter):
    DEFAULT_GROUP = '([^/]+)'

    def parse(self, path, shortcuts=None):
        """ @path: (#str) URI path
            @shortcuts: (#dict) |{shortcut_name: regex_pattern}|
            -> (#tuple(#str regex pattern, #list[regex groups])) """
        pattern = []
        add_pattern = pattern.append
        groups = []
        add_group = groups.append
        escape = re.escape
        shortcuts = shortcuts or {}
        for lit, field_name, regex, _ in super().parse(path):
            lit_ = ""
            for part in lit.split('\\*'):
                part_ = part.split('*')
                _group = "(.+)"
                for y in range(len(part_) - 1):
                    add_group((_group, None))
                lit_ += _group.join(escape(p) for p in part_)
            add_pattern(lit_)
            if field_name is not None and '(' in field_name:
                regex = field_name
                field_name = None
            if regex is not None and not regex:
                regex = self.DEFAULT_GROUP
            if regex:
                try:
                    regex = shortcuts[regex]
                except KeyError:
                    pass
                add_pattern(regex)
                add_group((regex, field_name or None))
        return (r"""%s(?:\?|(?:\/(?:\?|$))|$)""" % ''.join(pattern), groups)


class Router(object):
    """`Kola Router`

        Matches the REQUEST_URI or PATH_INFO with the correct
        :class:Route path for a given :class:Kola app.

        Basically, this parses a given route's path and translates it
        into a regex pattern. The best path is determined by the
        specificity of the route match and the number of matches
        occurring within the route pattern.

        =======================================================================
        ``Shortcuts``

        Several shortcut patterns are built in to the router for things
        like verifying an ID, slug or username. These shortcuts are
        specified in your URI pattern when creating the route.
        e.g. |@route('/users/{username:username}')|
        ..
            'slug': r'''([a-z0-9\-\_]+)''',           # slug-formatting_1
            'polite_slug': r'''([\w\-\_]+)''',        # Polite-Slug_Formattin2
            'strict_slug': r'''([a-z\-]+)''',         # strict-slug-formatting
            'num': r'''([\d]+)''',                    # 10
            'id': r'''([\d]+)''',                     # 10
            'uid': r'''([\d]{16,})''',                # 1061842104747033745
            'alpha': r'''([a-zA-Z]+)''',              # AdELkf
            'alnum': r'''([a-zA-Z0-9_]+)''',          # alDKElff3812_
            'rand': r'''([a-zA-Z0-9_-]+)''',          # alDKE-lff381_2
            'hashtag': string_tools.hashtag_pattern,  # word'swithsome_punc%
            'mention': string_tools.mentions_pattern, # @something
            'username': string_tools.username_pattern,# Grumpy_Rat
            'uuid': r'''([0-9a-fA-F\-]+)''',          # 7f14be65-be7c-4cfc-...
            'hex': r'''([0-9a-fA-F\-]+)'''            # 7f14be65be7c4cfc-...
        ..

        You can install your own route shortcuts via :meth:add_shortcut
    """
    __slots__ = ('routes', '_re_cache')
    shortcuts = {
        "slug": r"""([a-z0-9\-\_]+)""",             # slug-formatting_1
        "polite_slug": r"""([\w\-\_]+)""",          # Polite-Slug_Formatting2
        "strict_slug": r"""([a-z\-]+)""",           # strict-slug-formatting
        "num": r"""([\d]+)""",                      # 10
        "id": r"""([\d]+)""",                       # 10
        "uid": r"""([\d]{16,})""",                  # 1061842104747033745
        "alpha": r"""([a-zA-Z]+)""",                # AdELkf
        "alnum": r"""([\w]+)""",                    # alDKElff3812_
        "rand": r"""([a-zA-Z0-9_-]+)""",            # alDKE-lff381_2
        "hashtag": string_tools.hashtag_pattern,    # word'swithsome_punc%
        "mention": r"""(@\w{1,15})""",              # @something
        "username": r"""([a-zA-Z0-9_-]+)""",        # Grumpy_Rat
        "uuid": r"""([0-9a-fA-F\-]+)""",            # 7f14be65-be7c-4cfc-...
        "hex": r"""([0-9a-fA-F]+)"""                # 7f14be65be7c4cfc-...
    }
    _split_delimeters = re.compile(r"""\/|\?|\&|\=""").split
    _parser = RouteParser()
    _UriMatcher = namedtuple('UriMatcher', 'match groups')

    def __init__(self, *routes):
        self.routes = defaultdict(dict)
        if routes:
            self.add(*routes)
        self._re_cache = _re_cache()

    def copy(self):
        cls = self.__class__(*self.routes)
        return cls

    def clear(self):
        self.routes = defaultdict(dict)
        self._re_cache = _re_cache()

    def add_shortcut(self, *shortcuts):
        """ Adds one or many regex shortcuts
            @*shorcuts: repeating |'shortcut_name', r'''(pattern)'''| pairs
                e.g. |add_shortcut('my_shortcut', r'''my_pattern''')
        """
        self.shortcuts.update((k, v) for k, v in pairwise(shortcuts))

    def add(self, *routes):
        """ Adds one or multiple :class:Route to the router.
            @*routes: (:class:Route)
        """
        for route in routes:
            app, method = route.app, route.method
            try:
                self.routes[app][method].append(route)
            except KeyError:
                self.routes[app].update({method: []})
                self.routes[app][method].append(route)

    @memoize
    def get_rule(self, path):
        """ Parses the :class:Route path rules and converts them to a
            compiled regular expression. Each :class:Route is only parsed
            once and then cached locally.
        """
        pattern, groups = self._parser.parse(path, self.shortcuts)
        return self._UriMatcher(self._re_cache.get(pattern).match, groups)

    @lru_cache(65536)
    def find(self, app, method, path):
        """ Finds the first matching :class:Route for @app, @method and @path

            @app: (:class:Kola) instance
            @method: (#str) HTTP header REQUEST_METHOD
            @path: (#str) REQUEST_URI
            -> (#tuple) (:class:Route first matching pattern,
                         #list route group match vars,
                         #dict route |<named>| group match kwvars)
        """
        #: Finds the first route match
        for route in (self.routes[app].get(method) or []):
            rules = self.get_rule(route.path)
            match = rules.match(unquote(path))
            if match:
                #: Creates the vars to send to the route callback
                kwargs = {}
                args = []
                add_args = args.append
                for g, rg in zip(match.groups(), rules.groups):
                    g = unquote(g)
                    name = rg[1]
                    if name:
                        kwargs[name] = g
                    else:
                        add_args(g)
                return (route, args, kwargs)
        raise HTTPError(404, "Not found: " + repr(path))


class Route(object):
    """ =======================================================================
        ``Path Rules``

        - |*| matches any characters |(.+)| e.g. |@route("*")|
          or |@route("/*.html")|. These unnamed groups return as |*args| to
          the callback.
        - |{group_name}| returns |**kwargs (group_name={group_name})|
          to the callback. For example
          |@route("/api/user/{username}/{action}")|
          will return the keyword arguments
          |(username={username}, action={action})| to the callback function.
        - |{(^raw)}| regex goes in parentheses, anywhere you want to put it,
          with any regex you choose. When included in a named group
          it will add the rule to that group.
          For example |@route("/api/user/{username:(\w+)}/{action:(\d+)}")|
          will cause |{username}| to only accept |A-Za-z0-9_| characters,
          and |{action}| will only accept numeric characters.

        =======================================================================
        ``Shortcuts``

        Several shortcut patterns are built in to the router for things
        like verifying an ID, slug or username. These shortcuts are
        specified in your URI pattern when creating the route.
        e.g. |@route('/users/{uid:id}')| and |@route('/users/{:slug}')|

        ..
            'slug': r'''([a-z0-9\-\_]+)''',           # slug-formatting_1
            'polite_slug': r'''([\w\-\_]+)''',        # Polite-Slug_Formattin2
            'strict_slug': r'''([a-z\-]+)''',         # strict-slug-formatting
            'num': r'''([\d]+)''',                    # 10
            'id': r'''([\d]+)''',                     # 10
            'uid': r'''([\d]{16,})''',                # 1061842104747033745
            'alpha': r'''([a-zA-Z]+)''',              # AdELkf
            'alnum': r'''([a-zA-Z0-9_]+)''',          # alDKElff3812
            'rand': r'''([a-zA-Z0-9_-]+)''',          # alDKE-lff381_2
            'hashtag': string_tools.hashtag_pattern,  # word'swithsome_punc%
            'mention': string_tools.mentions_pattern, # @something
            'username': string_tools.username_pattern,# Grumpy_Rat
            'uuid': r'''([0-9a-fA-F\-]+)''',          # 7f14be65-be7c-4cfc-...
            'hex': r'''([0-9a-fA-F\-]+)'''            # 7f14be65be7c4cfc-...
        ..

        =======================================================================
        ``Callback & Plugin Rules``

        - Must accept the same number of arguments as there are
          named and unnamed groups specified in the route path
        - The callback returns whatever it is you are sending as a response
          to the WSGI handler, whether that be a dict, a :class:View,
          plain text, bytes, etc.

        =======================================================================
        ``Usage Example``

        - Uses a decorator to route to all request methods matching the URI
          |'/ping/{pong}'| where |{pong}| can only be the characters
          |A-Za-z0-9_|, with a callback bound to |ponger|
          ..
          from kola import *

          @route('/ping/{pong:(\w+)}')
          def ponger(pong=None):
              ''' -> kwarg pong=@pong '''
              return pong
          ..

        - Adds a route to GET requests with the REQUEST_URI
          |/ping/{pong}| where |{pong}| can only be the characters |0-9|,
          with a callback bound to |ponger|
          ..
          from kola import *

          kola = Kola()
          def ponger(pong=None):
              ''' Returns kwarg pong=@pong '''
              return pong
          kola.get('/ping/{pong:(\d+)}', ponger)
          ..

        - Adds several routes to |GET| requests, with several callbacks,
          defaulting to 404
          ..
          from kola import *

          kola = Kola()
          def ponger(pong):
              ''' Returns kwarg pong=@pong '''
              return pong

          def long_pong(pong1, pong2, pong3, long_pong=None):
              return "Pong!"

          def str_pong(*args):
              return args

          GET = [
              # Imports plugin from callable
              ('*', View(404)), # 404 default
              ('/ping/{pong:(\d+)}', ponger),
              # Imports plugin from string
              ('/ping/*', 'wsgi.str_pong'),
              ('/ping/*/*/{(\d+)}/{long_pong:((\w+).html$)}',
               'wsgi.long_pong'),
              ('/ping?pong={([a-z0-9_-]+)}', 'wsgi.ponger') ]

          # Adds the GET routes and their callbacks to the application
          kola.get(GET)
          ..

    """
    __slots__ = ('path', '_callback', '_plugins', 'method', 'ignore', 'app',
                 'schema', '_cache')

    def __init__(self, app, path, callback, plugins=None, method="GET",
                 ignore=None, schema=None):
        """ `Kola Route`
            Configurable route used for matching request URIs to their proper
            callbacks or :class:View.

            @app: (:class:Kola) instance to bind to.
            @path: (#str) path to match REQUEST_URI against.
            @callback: (#callable) callback to execute.
            @plugins: (#list or #tuple) of plugins to add to execute on the
                route, before the callback is called.
            @method: (#str) REQUEST_METHOD to listen on.
            @ignore: (#list) of plugins to ignore
            @schema: (:class:Schema) instance
        """
        self.path = path
        self._callback = self._import(callback)
        self._plugins = list(plugins) if plugins else []
        self.method = method.upper()
        self.ignore = set(ignore or [])
        self.app = app
        self.schema = schema
        self._cache = {}

    __repr__ = preprX('method', 'path', '_callback', keyless=True,
                      address=False)

    def copy(self):
        return self.__class__(self.app, self.path, self._callback,
                              self._plugins, self.method)

    @staticmethod
    @memoize
    def _import(obj_str):
        return import_from(obj_str)

    @DictProperty('_cache', 'plugins', read_only=True)
    def plugins(self):
        def is_plugin(plugin):
            if hasattr(plugin, 'label'):
                return plugin.label not in self.ignore
            return True

        def cast(plugin):
            if isinstance(plugin, str):
                plugin = self._import(plugin)
            if hasattr(plugin, 'setup'):
                plugin.setup(self)
            return plugin.apply if hasattr(plugin, 'apply') else plugin

        return tuple(filter(is_plugin, map(cast, self._plugins)))

    @DictProperty('_cache', 'closable_plugins', read_only=True)
    def closable_plugins(self, *args, **kwargs):
        return tuple(filter(lambda x: hasattr(x, 'close'), self._plugins))

    def close(self):
        for plugin in self.closable_plugins:
            plugin.close()

    def call(self, *args, **kwargs):
        """ Passes the route @args and @kwargs unpacked through
            installed plugins, and then to the callback
        """
        for plugin in self.plugins:
            plugin(self)

        result = self._callback(*args, **kwargs)

        return result
