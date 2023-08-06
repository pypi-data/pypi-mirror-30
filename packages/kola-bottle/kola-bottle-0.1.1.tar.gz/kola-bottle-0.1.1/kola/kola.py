import time
import inspect
from traceback import format_exc
from collections import UserList
from threading import current_thread

from vital.debug import preprX, line
from vital.tools import encoding

from kola.appstack import apps
from kola.conf import config
from kola.exceptions import *
from kola.serializers import dumps
from kola.requests import request
from kola.responses import response, HTTPError
from kola.routing import *
from kola.loggers import *
from kola.wsgi import HTTP_STATUS_LINES, WSGIRefServer


__all__ = ('Kola', 'Schema')


class Kola(object):
    """ =======================================================================
        ``Kola Usage``

        Multiple instances
        ..
            from kola import * # Imports __all__
            web_app = Kola('/path/to/your/@config_file.json', name="app1")
            web_app2 = Kola('/path/to/your/@config_file.json', name="app2")
            web_api = Kola('/path/to/your/@config_file2.json')
        ..


        Enter(executed prior to routing) and
        Exit(excuted just before the response is returned) hooks
        ..
        @enter
        def hello():
            response.set_header('access-control-allow-credentials', 'true')

        @exit
        def goodbye():
            response.set_header('x-app-runtime', timer.stop())
        ..


        RESTful routing with plugins and callbacks via :class:Route
        ..
        # Accepts lists of (route_path, callback) pairs
        GET = [("/user/<username(\w+)>", UserController),]
        api_handler.get(GET, RouteDefaultCallback)

        # Accepts decorators with and without paths
        @options
        def OPTIONS(x):
            return

        @post("/<user_id(\d+)>/<action>")
        def PostRouteCallback(x):
            return
        ..

        ©2015, Bottle, Marcel Hellkamp
        ©2015, Refactor by Jared Lunde
    """
    __slots__ = ('config_file', '_name', 'routes', 'router', '_autojson',
                 'catchall', 'plugins', 'debug', 'hooks', 'schemas')

    def __init__(self, config_file=None, name=None, catchall=True,
                 autojson=None, templates=None, debug=False,
                 plugins=None, router=None, routes=None):
        """ `Kola`
            ==================================================================
            A fast and feature-rich fork of the WSGI framework Bottle.
            (http://bottlepy.org/docs/dev/index.html)

            This class loads creates a new Kola application.

            @config_file: (#str) configuration file to bind the instance to.
            @name: (#str) name of the app
            @catchall: (#bool) to catch all request and response errors
                or let them raise.
            @autojson: (#bool) |True| to auto respond with JSON when a dict,
                list or other iterable or map, or an object with a |for_json|
                or |to_json| method,is returned in your route callback. A
                #dict configuration may also be provided in your kola.json
                file.
                ..
                # AutoJSON configuration example,
                # can also be added to kola.json
                "autojson": {
                    "bigint_as_string": False,
                    "encode_html_chars": True
                }
            @debug: (#bool) to display Kola debug info each request
            @plugins: (#list or #tuple) of plugins which execute
                in :class:Route prior to sending a response, and
                close after the route callback is executed
            @router:(:class:Router)
            @routes: (#list or #tuple) of :class:Route objects
        """
        config.bind(config_file)
        self.config_file = config_file or config.file
        self._name = name
        self._autojson = autojson
        self.catchall = catchall
        self.debug = debug
        self.hooks = {}
        # Middleware plugins, instantiated right before main callback
        self.plugins = list(plugins or [])
        # Add the app to the stack
        apps.push(self)
        # List of installed :class:Route instances.
        self.routes = list(routes) if routes else []
        # Maps requests to :class:Route instances.
        self.router = router or Router()
        self.router.add(*self.routes)
        # Schemas
        self.schemas = []

    __repr__ = preprX('name', address=False, keyless=True)

    @property
    def config(self):
        """ The configuration file bound to this Kola application.
            -> :var:config
        """
        thread = current_thread()
        if config.file != self.config_file or not config.is_bound(thread):
            config.bind(self.config_file, thread)
        return config

    @property
    def name(self):
        return self._name or (
            self.config.get("appname") if config else "KolaApp")

    @property
    def version(self):
        return self.config.get('version')

    @property
    def autojson(self):
        return self._autojson if self._autojson is not None else \
            self.config.get('autojson', True)

    def install(self, *plugins):
        """ Installs @plugins/middleware which execute before your
            callback during routing.

            @plugins: #callable objects which accept |*args| and |**kwargs|
                related to unnamed (.*) groups and <named(.*)> groups
                specified in the :class:Route
        """
        self.plugins.extend(plugins)

    def uninstall(self, *plugins):
        """ Removes specified installed @plugins

            @plugins: #callable objects which you've installed to
                this application
        """
        for plugin in plugins:
            self.plugins.remove(plugin)

    def add_schema(self, *schemas):
        """ Installs @schemas to the this instance

            @schemas: :class:Schema instances
        """
        self.schemas.extend(schemas)

    def remove_schema(self, *schemas):
        """ Removes specified installed @schemas

            @schemas: :class:Schema instances
        """
        for schema in schemas:
            self.schemas.remove(schema)

    def add_hook(self, name, callback):
        """ Adds an enter or exit hook to the instance.

            @name: #str "enter" or "exit"
            @callback: #callable
            @args: args to pass to the hook
            @kwargs: kwargs to pass to the hook
        """
        self.hooks[name] = callback

    def hook(self, name):
        def _hook(callback):
            self.add_hook(name, callback)
            return callback
        return _hook

    def _execute_hook(self, name):
        self.hooks.get(name, lambda: None)()

    def enter(self, callback):
        """ Adds enter hook with specified @*args, @**kwargs

            @callback: (#callable) to execute before request
        """
        self.add_hook("enter", callback)

    def exit(self, callback):
        """ Adds exit hook with specified @*args, @**kwargs

            @callback: (#callable) to execute after request
        """
        self.add_hook("exit", callback)

    def get(self, *args, **kwargs):
        """ Adds GET route(s) to the instance

            @paths: #str router path pattern. See :class:Route
            @callback: #callable object to execute when the @paths are matched,
                directly prior to sending a response. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route
            @plugins: #list or #tuple of plugins to execute before the
                @callback is run. This gets appended to the plugins already
                installed on the application. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route

            ..
                from kola import Kola, get

                web_app = Kola()

                @get("*")
                def some_func(*args):
                    return ""

                kola.get("/users/*", lambda x: return "")
            ..
        """
        self.route(*args, method="GET", **kwargs)

    def post(self, *args, **kwargs):
        """ Adds POST route(s) to the instance

            @paths: #str router path pattern. See :class:Route
            @callback: #callable object to execute when the @paths are matched,
                directly prior to sending a response. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route
            @plugins: #list or #tuple of plugins to execute before the
                @callback is run. This gets appended to the plugins already
                installed on the application. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route

            ..
                from kola import Kola, post

                web_app = Kola()

                @post("*")
                def some_func(*args):
                    return ""

                kola.post("/users/*", lambda x: return "")
            ..
        """
        self.route(*args, method="POST", **kwargs)

    def put(self, *args, **kwargs):
        """ Adds PUT route(s) to the instance

            @paths: #str router path pattern. See :class:Route
            @callback: #callable object to execute when the @paths are matched,
                directly prior to sending a response. Must accept |*args|
                and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route
            @plugins: #list or #tuple of plugins to execute before the
                @callback is run. This gets appended to the plugins already
                installed on the application. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route

            ..
                from kola import Kola, put

                web_app = Kola()

                @put("*")
                def some_func(*args):
                    return ""

                kola.put("/users/*", lambda x: return "")
            ..
        """
        self.route(*args, method="PUT", **kwargs)

    def options(self, *args, **kwargs):
        """ Adds OPTIONS route(s) to the instance

            @paths: #str router path pattern. See :class:Route
            @callback: #callable object to execute when the @paths are matched,
                directly prior to sending a response. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route
            @plugins: #list or #tuple of plugins to execute before the
                @callback is run. This gets appended to the plugins already
                installed on the application. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route

            ..
                from kola import Kola, options

                web_app = Kola()

                @options("*")
                def some_func(*args):
                    return ""

                kola.put("/users/*", lambda x: return "")
            ..
        """
        self.route(*args, method="OPTIONS", **kwargs)

    def patch(self, *args, **kwargs):
        """ Adds PATCH route(s) to the instance

            @paths: #str router path pattern. See :class:Route
            @callback: #callable object to execute when the @paths are matched,
                directly prior to sending a response. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route
            @plugins: #list or #tuple of plugins to execute before the
                @callback is run. This gets appended to the plugins already
                installed on the application. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route

            ..
                from kola import Kola, patch

                web_app = Kola()

                @patch("*")
                def some_func(*args):
                    return ""

                kola.patch("/users/*", lambda x: return "")
            ..
        """
        self.route(*args, method="PATCH", **kwargs)

    def delete(self, *args, **kwargs):
        """ Adds DELETE route(s) to the instance

            @paths: #str router path pattern. See :class:Route
            @callback: #callable object to execute when the @paths are matched,
                directly prior to sending a response. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route
            @plugins: #list or #tuple of plugins to execute before the
                @callback is run. This gets appended to the plugins already
                installed on the application. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route

            ..
                from kola import Kola, delete

                web_app = Kola()

                @delete("*")
                def some_func(*args):
                    return ""

                kola.delete("/users/*", lambda x: return "")
            ..
        """
        self.route(*args, method="DELETE", **kwargs)

    def route(self, paths, callback=None, plugins=None, ignore=None,
              schema=None, method="GET"):
        """ Adds route(s) to the instance.

            @paths: (#str or #list) of #str router path pattern. See :class:Route
            @callback: (#callable) object to execute when the @paths are
                matched, directly prior to sending a response. Callback must
                accept  matched |*args| and |**kwargs| related to unnamed
                |(.*)| groups and |<named(.*)>| groups specified in the
                :class:Route.
            @plugins: (#list or #tuple) of plugins to execute before the
                @callback is run. This gets appended to the plugins already
                installed on the application. Must accept matched
                |*args| and |**kwargs| related to unnamed |(.*)| groups and
                |<named(.*)>| groups specified in the :class:Route
            @ignore: (#list) of plugins to ignore
            @schema: (:class:Schema) to apply to the route
            @method: (#str, #list, #set or #tuple) of request methods. Either
                GET, POST, PUT, OPTIONS, PATCH, or DELETE, or a combination
                of any
        """
        routes = []
        plugins = self.plugins + (list(plugins or []))
        add_route = routes.append
        if method == "*":
            method = ("GET",  "POST", "PATCH", "DELETE", "PUT", "OPTIONS")
        methods = method if isinstance(method, (tuple, list)) else [method]
        for path in (paths if isinstance(paths, (tuple, list)) else [paths]):
            if isinstance(path, (tuple, list)):
                path, callback = path
            for _method in methods:
                add_route(Route(
                    self, path, callback=callback, plugins=plugins,
                    method=_method, ignore=ignore, schema=schema))
        self.router.add(*routes)
        self.routes.extend(routes)

    def print_routes(self):
        """ Prints all of the :class:Route objects assigned to this
            application.
        """
        line("—")
        logg(self).warning("Kola", force=True)
        line("—")
        for app, methods in self.router.routes.items():
            for method, routes in methods.items():
                logg(routes).notice(method, force=True)
                line(" ")
        line("—")

    def _json(self, output):
        """ Automatically converts response to JSON object if turned on. """
        if isinstance(output, (str, bytes, int, float)):
            return output
        response.set_content_type("application/json")
        options = self.config.get('autojson', {})
        if hasattr(output, 'to_json'):
            json_response = output.to_json()
        elif hasattr(output, 'for_json'):
            json_response = dumps(output.for_json(), **options)
        else:
            json_response = dumps(output, **options)
        #: JSONp support when query string contains "callback"
        #  and "jsonp" in ?callback=..jsonp..
        callback = request.query.get('callback')
        if callback and 'jsonp' in callback:
            response.set_content_type("application/javascript")
            # JSONp formatting _jsonpcallback({obj})
            json_response = '%s(%s)' % (callback, json_response)
        return json_response

    def _handle_request(self, environ):
        """ Handles the WSGI request """
        path = environ['PATH_INFO']
        route = None

        try:
            environ['PATH_INFO'] = path.encode('latin1').decode('utf8')
        except UnicodeError:
            return (HTTPError(400,
                              'Invalid path string. Expected UTF-8'), self)
        try:
            environ['kola.app'] = self
            #: Binds the request and response objects
            request.bind(environ)
            response.bind()
            #: Finds the correct route
            uri = environ.get("REQUEST_URI", environ.get("PATH_INFO", "/"))
            route, args, kwargs = self.router.find(self, request.method, uri)
            request.route = route
            #: Determines which app schema to use
            app = self if not route.schema else route.schema
            #: Binds configuration
            app.config
            #: Initialization hook
            app._execute_hook("enter")
            #: Route the request
            return (route.call(*args, **kwargs), route, app)
        except HTTPRedirect:
            return (None, self)
        except HTTPError as e:
            return (self._err(e.body, e._status_code), route, self)
        except (KeyboardInterrupt, SystemExit, MemoryError):
            if not self.catchall:
                raise
            return (self._err(format_exc()), route, self)
        except Exception as e:
            if not self.catchall:
                raise
            stacktrace = format_exc()
            environ['wsgi.errors'].write(stacktrace)
            err_code = e.status_code if hasattr(e, 'status_code') else 500
            return (self._err(stacktrace, err_code), route, self)

    def _handle_response(self, output):
        """ Handles the WSGI response and json encodes it if :prop:autojson
            is True
        """
        # Empty output is done here
        if output is None:
            response['Content-Length'] = \
                response.get_header('Content-Length', 0)
            return ""
        # Byte Strings are just returned
        if isinstance(output, bytes):
            response['Content-Length'] = len(output)
            response.body = output
            return response.body
        # AutoJSON if dict, list, etc
        if self.autojson:
            output = self._json(output)
        # Encode unicode strings
        if isinstance(output, str):
            output = output.encode(response.charset)
        # File-like objects.
        if hasattr(output, 'read'):
            if 'wsgi.file_wrapper' in request.environ:
                return request.environ['wsgi.file_wrapper'](output)
            elif hasattr(output, 'close') or not hasattr(output, '__iter__'):
                return WSGIFileWrapper(output)
        else:
            response.body = output
        return response.body

    def _err(self, err, err_code=500):
        """ Exception response outputs """
        response.set_status(err_code)
        if self.debug:
            logg(err).error()
            message = ("<html><head><style>pre{}</style></head>"
                       "<body style='text-align:center'><h1>Error: {}</h1>"
                       "<pre style='width: 400px'>"
                       "{}</pre></html>"
                       ).format("{font-family:'hack', 'monospace';"
                                "font-size:0.8em}",
                                HTTP_STATUS_LINES[err_code],
                                err)
            return encoding.uniorbytes(message, bytes)
        return encoding.uniorbytes(
            "<pre>Error {}</pre>".format(err_code), bytes)

    def wsgi(self, environ, start_response):
        """ The Kola WSGI-interface. Routes and handles the WSGI request and
            response.

            -> :class:HTTPResponse
        """
        try:
            #: Handles the request
            resp, route, app = self._handle_request(environ)
            #: Exit hook
            app._execute_hook('exit')
            #: Close route
            if route is not None:
                route.close()
            #: Handles the response
            resp = app._handle_response(resp)
            #: rfc2616 section 4.3
            if response._status_code in {100, 101, 204, 304} or \
               environ['REQUEST_METHOD'] == 'HEAD':
                if hasattr(resp, 'close'):
                    resp.close()
                resp = []
            start_response(response.status_line, response.listheaders())
            #: The response (must be wrapped in list)
            return [resp]
        except (KeyboardInterrupt, SystemExit, MemoryError):
            return [self._err(format_exc())]
        except Exception:
            if not self.catchall:
                raise
            return [self._err(format_exc())]

    __call__ = wsgi

    def print_state(self):
        """ Debugs the request and response by calling relevant
            methods and running through :class:vital.debug.Logg
        """
        logg(request.method).notice("Request method", force=True)
        logg(request.content_type).notice("Request content type", force=True)
        logg(request.get_cookies()).notice("Request cookies", force=True)
        logg(request.chunked).notice("Request is chunked?", force=True)
        logg(request.is_xhr).notice("Request is xhr?", force=True)
        logg(request.GET).notice("Request query string", force=True)
        logg(request.POST).notice("Request POST data", force=True)
        logg(request.files).notice("Request files", force=True)
        logg(request.user_agent).notice("Request user agent", force=True)
        logg(request.body).notice("Request body", force=True)
        logg(request.json).notice("Request json", force=True)
        logg(request.location).notice("Request location", force=True)
        logg(request.content_length).notice(
            "Request content_length", force=True)
        line()
        logg(response).notice("Response", force=True)
        line()
        logg(session).notice("Session", force=True)
        line()

    def run(self, port=8000, quiet=False, **kwargs):
        httpd = WSGIRefServer(port=port, quiet=quiet, **kwargs)
        print("Serving on port %s:" % port)
        # WSGIRefServer(host=0.0.0.0, port=8000, )
        # Serving on port 8000:
        httpd.run(self)
        # --Request to http://host:8000/--
        # 60.120.123.00 - - [18/Sep/2015 18:47:17] "GET / HTTP/1.1" ...
        #   -> Hello world. Welcome to Kola Bottle.


#: Adds default app to appstack
Kola()


class Schema(Kola):
    """ ======================================================================
        ``Usage Example``
        ..
            from kola import *

            #: WSGI handler / base instance
            cool_api = Kola('/path/to/cool_api.json')
            cool_api.get('/ping/<pong>', lambda pong: pong.upper())

            #: Api v1
            cool_api_v1 = Schema('v1', cool_api, '/v1')

            #: Api v2
            cool_api_v2 = Schema('v2', cool_api, '/v2')
            # v2 inherits routes from cool_api, where /ping/pong becomes
            # /v2/ping/pong
            cool_api_v2.inherit_routes()

            #: Pathless extension schema
            cool_api_ext = Schema('some_extension', cool_api)
            #: Creates route and callback specific to cool_api_ext's config
            #  which can be executed at /ping/<pong>
            cool_api_ext.get('/ping/<pong>', lambda pong: pong.lower())
        ..
    """

    def __init__(self, name, parent=None, path=None, **config):
        """ `Kola Schema`
            Creates a schema within your :class:Kola apps which can have
            configurations and routes independent of the parent application.

            @name: (#str) name of the schema. Used for referencing in things
                like :func:url_for
                ..
                    url_for(
                        'users', 'parent_name.schema_name',
                        {'username': 'fred'})
                ..
                |/schema_path/users/fred                   |
            @parent: (:class:Kola) parent instance which handles to the WSGI
                requests.
            @path: (#str) base path name to append routes within this
                schema with

            @**config: keyword arguments to super() to :class:Kola
        """
        super().__init__(name=name, **config)
        self.parent = None
        self._thanks_dad(parent, config)
        self.path = ('/' + path.strip('/')) if path else ""
        self.routes = self.config.get('routes', [])
        self.router = self.router.copy()
        self.router.clear()
        self.router.add(*self.routes)
        self.parent.add_schema(self)

    __repr__ = preprX('name', 'path', 'parent', address=False, keyless=True)

    def _thanks_dad(self, parent, config=None):
        """ Inherits the options of @parent into this schema if they aren't
            defined already by this schema's @config
        """
        self.parent = parent
        ignore = {'name', 'schemas'}
        for key in dir(parent):
            attr = getattr(parent, key)
            if not key.endswith("__") and not inspect.isroutine(attr) \
               and key not in ignore:
                if not config or key not in config:
                    try:
                        setattr(self, key, attr)
                    except AttributeError:
                        pass

    def inherit_routes(self, from_=None):
        """ Transforms @from_ routes to this schema's routes. If no @from_ is
            present, :prop:parent will be used.

            @from_: (:class:Kola or :class:Schema)
        """
        from_ = from_ or self.parent
        routes = []
        add_route = routes.append
        for route in (from_.routes):
            route = route.copy()
            route.path = self._merge_path(route.path)
            route.schema = self
            route._plugins = self.plugins
            add_route(route)
        self.routes.extend(routes)
        self.router.add(*routes)
        self.parent.router.add(*routes)

    def _merge_path(self, path):
        return '{}{}'.format(self.path, path)

    def route(self, paths, callback=None, plugins=None, ignore=None,
              method="GET"):
        """ :see::meth:Kola.route """
        routes = []
        plugins = self.plugins + (list(plugins) if plugins else [])
        add_route = routes.append
        if method == "*":
            method = ("GET",  "POST", "PATCH", "DELETE", "PUT", "OPTIONS")
        methods = method if isinstance(method, (tuple, list)) else [method]
        for path in (paths if isinstance(paths, (tuple, list)) else [paths]):
            if isinstance(path, (tuple, list)):
                path, callback = path
            for _method in methods:
                add_route(Route(
                    self.parent, self._merge_path(path), callback=callback,
                    plugins=plugins, method=_method, ignore=ignore,
                    schema=self))
        self.router.add(*routes)
        self.routes.extend(routes)
        self.parent.router.add(*routes)
