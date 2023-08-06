from collections import OrderedDict
from functools import lru_cache

import bleach
import markdown
import jinja2

from vital.cache import memoize, local_expiring_lru, local_lru
from vital.tools import html, import_from
from vital.debug import preprX, cut

from kola.appstack import apps
from kola.conf import config
from kola.kola import Schema
from kola.serializers import dumps, loads
from kola.responses import response
from kola.requests import request
from kola.shortcuts import redirect, abort


__all__ = ('Template', 'template', 'View', 'url_for', 'link_for')


#
#  ``Templates``
#
class Template(object):
    """ A thin wrapper for :mod:jinja2 templates with a local LRU
        cache in the front.

        Configurable via the kola configuration file. Key/value maps
        aside from |path| and |markdown| are passed along to
        :class:jinja2.Environment. |markdown| is passed to
        :class:markdown.Markdown

        Also builds several filters and globals into the Jinja2 environment:
            - jsonify: :func:dumps
            - unjsonify: :func:loads
            - markdown: :class:markdown.Markdown
            - url_for: :func:url_for
            - link_for: :func:link_for
            - bleach: :func:bleach.clean
            - linkify: :func:bleach.linkify
            - cut: :func:cut

        Additional filters and globals can be added via the template config
            ..
            # options not specified above are passed to jinja2.Environment
            "templates": {
                "path": "/home/jared/apps/cool_app/cool_app/views",
                "extensions": ["jinja2.ext.autoescape"],
                "compress": false,
                "filters": {
                    "filter_name": "filter.full_callable.path"
                },
                "globals": {
                    "global_name": "global.full_callable.path"
                }
            }
            ..
    """
    __slots__ = ("_path", "_compress", "_markdown", "_options", "__cache_size",
                 "label")
    _cache = OrderedDict()
    _reserved = {'markdown', 'options', 'compress', 'path', 'label',
                 'cache_size'}

    def __init__(self, path=None, compress=None, markdown=None,
                 label='templates', cache_size=None, **env_options):
        """ `Kola Templates`

            @path: (#str) :class:jinja2.FileSystemLoader searchpath
            @compress: (#bool) removes whitespace from response if True
            @markdown: (#dict) unpacked keyword arguments to pass to
                :class:markdown.Markdown. If None are specified, markdown will
                be an unavailable filter in the template
            @label: (#str) keyname to search for in kola.json
            @cache_size: (#int) LRU cache size for rendered templates
            @**env_options: keyword arguments to send to
                :class:jinja2.Environment
        """
        self.label = label
        self._options = env_options
        self._compress = compress
        self._markdown = markdown
        self._path = path
        self.__cache_size = cache_size or 0

    __repr__ = preprX('path', keyless=True, address=False)

    @property
    def config(self):
        return config.get(self.label, {})

    @property
    def path(self):
        return self.config.get('path', './') if not self._path else self._path

    @property
    def options(self):
        opt = {k: v
               for k, v in self.config.items()
               if k not in self._reserved}
        return opt if not self._options else self._options

    @property
    def compress(self):
        return self.config.get('compress', False) if self._compress is None \
            else self._compress

    @property
    def markdown(self):
        return self.config.get('markdown', {}) if self._markdown is None \
            else self._markdown

    @property
    def _cache_size(self):
        return self.config.get('cache_size', 10240) \
            if self.__cache_size is None else self.__cache_size

    @memoize
    def loader(self, path):
        return jinja2.FileSystemLoader(searchpath=path)

    @memoize
    def get_environment(self, path, options):
        _filters = options.get('filters', {})
        _globals = options.get('globals', {})
        if 'filters' in options:
            del options['filters']
        if 'globals' in options:
            del options['globals']
        env = jinja2.Environment(loader=self.loader(path), **options)
        json_opt = self.config.get('autojson', {})
        env.filters['jsonify'] = lambda x: dumps(x, **json_opt)
        env.filters['unjsonify'] = loads
        if self.markdown:
            md_args = {} if isinstance(self.markdown, bool) else self.markdown
            md = markdown.Markdown(**md_args)
            env.filters['markdown'] = lambda text: \
                jinja2.Markup(md.convert(text))
        env.globals['url_for'] = url_for
        env.globals['link_for'] = link_for
        env.globals['bleach'] = bleach.clean
        env.globals['linkify'] = bleach.linkify
        env.globals['cut'] = cut
        env.filters.update({k: (import_from(v) if isinstance(v, str) else v)
                            for k, v in _filters.items()})
        env.globals.update({k: (import_from(v) if isinstance(v, str) else v)
                            for k, v in _globals.items()})
        return env

    @local_lru
    def render(self, file=None, **kwargs):
        """ Renders the given template @file
            -> a rendered :mod:jinja2 template
        """
        environment = self.get_environment(self.path, self.options)
        tpl = environment.get_template(file)
        rendered_template = tpl.render(**kwargs)
        return html.remove_whitespace(rendered_template) \
            if self.compress else rendered_template


template = Template()


class View(object):
    """ Passes keyword arguments for the thread :var:request,
        :var:response, and :prop:app through to the
        template via their respective names.

        ======================================================================
        ``Usage Example``
            ..
            from kola import Kola, View
            web_handler = Kola("/path/to/kola.json")

            view = View('home', status_code=200)
            # -> template.render(
            #       'pages/home.tpl',
            #        app=request.environ['kola.app'],
            #        request=request,
            #        response=response)
            web_handler.get("/", view)
            ..

        Configurable via the kola configuration file. Key/value maps
        aside from |path| and |markdown| are passed along to
        :class:jinja2.Environment. |markdown| is passed to
        :class:markdown.Markdown

        Also builds several filters and globals into the Jinja2 environment:
            - jsonify: :func:dumps
            - unjsonify: :func:loads
            - markdown: :class:markdown.Markdown
            - url_for: :func:url_for
            - link_for: :func:link_for
            - bleach: :func:bleach.clean
            - linkify: :func:bleach.linkify
            - cut: :func:cut

        Additional filters and globals can be added via the template config
            ..
            # options not specified above are passed to jinja2.Environment
            "templates": {
                "path": "/home/jared/apps/cool_app/cool_app/views",
                "extensions": ["jinja2.ext.autoescape"],
                "compress": false,
                # Filters example
                "filters": {
                    "filter_name": "filter.full_callable.path",
                    "camel_to_underscore":
                        "vital.tools.strings.camel_to_underscore"
                },
                # Globals example
                "globals": {
                    "global_name": "global.full_callable.path",
                    "cut": "vital.debug.cut"
                }
            }
            ..
    """
    __slots__ = ('tpl_file', 'tpl_path', 'tpl', 'name', 'plugins',
                 'state', 'aborted', 'redirected', 'status_code')

    def __init__(self, tpl, *plugins, name=None, cache_ttl=0, cache_size=0,
                 tpl_path=None, status_code=None):
        """ `Kola Views`
            ==================================================================
            A versatile template class which allows you to use :func:url_for
            and :func:link_for, in addition to automatically providing
            templates with access to information about the app including the
            uWSGI app receiving the request, that app's config file and the
            WSGI :var:request and :prop: response objects.
            ==================================================================
            @tpl: (#str) the name of the template file relative to @tpl_path,
                does not require that you include a .tpl extension
            @plugins: (#list) of plugins called prior to rendering the template
                and receive the current View as an argument
            @name: (#str) the name of the template. Used for :func:url_for and
                :func:link_for. If no name is specified, @tpl is used
            @cache_ttl: (#int) locally caches rendered pages for the given ttl,
                must be used with @cache_size. Should not be used on dynamic
                pages.
            @cache_size: (#int) maximum size of the local template lru cache,
                must be used with @cache_ttl
            @tpl_path: (#str) the path relative to the jinja2 environment in
                :class:BaseTemplate where the template file is located
            @status_code: (#int) status code to set the
        """
        self.tpl_file = tpl.replace(".tpl", "")
        if tpl_path:
            self.tpl_path = tpl_path.strip("/") + '/'
        else:
            self.tpl_path = ""
        self.tpl = "{}{}.tpl".format(self.tpl_path, self.tpl_file)
        self.name = name or self.tpl_file.lstrip("/")
        self.plugins = list(plugins or [])
        self.state = {}
        self.aborted = False
        self.redirected = False
        self.status_code = None

    __repr__ = preprX('name', 'tpl', 'state', keyless=True, address=True)

    def __call__(self, *uri_args, **uri_kwargs):
        """ Renders a jinja2 template with data received from the URI
            and :prop:plugins.

            @uri_args: unnamed groups received from :class:Route, these
                are completely ignored
            @uri_kwargs: named groups received from :class:Route

            :see::meth:render
        """
        try:
            if int(self.tpl_file) > 0:
                response.set_status(int(self.tpl_file))
        except ValueError:
            pass
        return self.render(**uri_kwargs)

    def install(self, *plugins):
        """ Plugins are called prior to rendering the template and receive
            the request routing |*args| and |**kwargs| as arguments.

            @plugins must return a #dict or #None
        """
        self.plugins.extend(plugins)

    def redirect(self, url, code=None):
        """ Allows redirection from plugins before hitting the view.
            :see::var:redirect
        """
        redirect(url, code=code)
        self.redirected = True

    def abort(self, code=500, text=None):
        """ Allows plugins to abort execution before hitting the view.
            :see::var:redirect
        """
        abort(code, text)
        self.aborted = True

    def render(self, **state):
        """ Renders a data in @**state

            @**state: keyword arguments to pass to the template

            Data is unpacked into the template via @**state. This data
            can be manipulated via :meth:install(ed) plugins, as the |View|
            instance is passed to each plugin as the plugin's only argument.
            The state of the data being passed to the view is controlled by
            the |state| attribute in the view.
            ..
                def your_plugin(view):
                    print(view.state) # Prints the data state of the view
            ..

            Additionally, keyword arguments for the thread :var:request,
            :var:response, :var:app, and :var:session are passed through
            to the template via their respective names.

            The template is passed on to each plugin as an argument.

            ==================================================================
            ``Usage Example``
            ..
                #: Request /users/jared/post is routed to the following:
                @route("/users/<username(.*)>/(.*)", users_action_view)
                def some_callback(*arg_action, **username):
                    print(username, arg_action)
                    #  {"username": jared} (post,)
                    users_action_view = View('users', name="users_actions")
                    username["success"] = True
                    return users_action_view(*arg_action, **username)
            ..
        """
        self.state = state
        for plugin in self.plugins:
            if hasattr(plugin, 'apply'):
                plugin.apply(self)
            else:
                plugin(self)
        if self.status_code:
            response.set_status(self.status_code)
        if self.aborted or self.redirected:
            return ""
        return template.render(self.tpl,
                               app=request.environ['kola.app'],
                               request=request,
                               response=response,
                               **self.state)


@lru_cache(maxsize=10000)
def _create_uri_path(route, path, with_hostname=False, **kwargs):
    path_re = route.app.router._re_cache.get(r"\{([\w]+).*?\}")
    if not kwargs:
        return (path_re.sub("", path), [1])
    else:
        matches = []
        add_match = matches.append
        for match in path_re.finditer(path):
            if match.group(1) in kwargs:
                add_match(match.group(1))
                path = path.replace(
                    match.group(0),
                    str(kwargs[match.group(1)]))
        if matches:
            if with_hostname:
                path = "{}://{}{}".format(
                    route.app.config.get("scheme",
                                         request.environ.get('wsgi.url_scheme',
                                                             'http')),
                    route.app.config.get("hostname",
                                         request.environ.get('HTTP_HOST')),
                    path
                )
            return (path, matches)


def url_for(endpoint, appname=None, with_hostname=False, with_matches=False,
            **kwargs):
    """ Automatically generates a URI based on @endpoint and keyword arguments
        given.

        @endpoint: name of the template or the name of the
            first /group/ of the URI.
        @appname: #str name of the app to look in
        @with_hostname: #bool whether or not to include a hostname with
            the URL
        @with_matches: #bool whether or to return the resulting URL
            in a tuple with its matched arguments |('/your/uri', ['match'])|
        @kwargs: named groups from the router e.g. |/users/{uid:id}|
            would be |url_for('users', uid=1234)|

        The parser first looks for a :class:View with a name
        matching endpoint and route groups that match the given
        @**kwargs.

        If it doesn't find a match, it tests the endpoint against the
        first /group/ of the route URIs and matches the rest of the route
        groups against given @**kwargs.

        ======================================================================
        ``Usage Example``
        ..
            from kola import Kola, url_for

            app1 = Kola(name="app1")
            app1.route("/u/{username:([\w]+)}", View("users"), method="GET")
            app1.route("/uid/{user_id:([\d]+)}", View("users"), method="GET")

            app2 = Kola(name="app2", routes=app1.routes)
            app2.route("/post/{pid:id}", View("posts"), method="GET")

            url_for("users", username="Bob")
            # -> "/u/Bob"

            url_for("users", user_id=1720, with_hostname=True)
            # -> "http://foo.bar/uid/1720"

            url_for("users", user_id=1720, with_hostname=True)
            # -> "http://foo.bar/uid/1720"

            url_for("posts", pid=1720, appname="app1")
            # -> None

            url_for("posts", pid=1720, appname="app2")
            # -> "/post/1720"

            url_for("post", pid=1720, appname="app2")
            # -> "/post/1720"
        ..
    """
    endpoint = endpoint.strip()
    kwargs = {k: v for k, v in kwargs.items() if k not in {'class_name', 'id'}}
    kola_apps = []
    add_app = kola_apps.append
    len_parts = 0
    appname_parts = []
    if appname:
        appname_parts = appname.split('.')
        len_parts = len(appname_parts)
    for _app in apps:
        if not appname or (len_parts and _app.name == appname_parts[0]):
            if len_parts > 1:
                for schema in _app.schemas:
                    if ".".join(appname_parts[1:]) == schema.name:
                        add_app(schema)
            else:
                add_app(_app)
    results = []
    add_result = results.append
    for kola_app in kola_apps:
        for route in kola_app.routes:
            if isinstance(route._callback, View):
                tpl = route._callback.name.strip()
                if tpl == endpoint:
                    result = _create_uri_path(route,
                                              route.path,
                                              with_hostname=with_hostname,
                                              **kwargs)
                    if result:
                        add_result(result)
        if results:
            results = sorted(results, key=lambda x: len(x[1]), reverse=True)
            if with_matches:
                return results[0]
            else:
                return results[0][0]
    for kola_app in kola_apps:
        is_schema = isinstance(kola_app, Schema)
        for route in kola_app.routes:
            path = route.path
            if is_schema and kola_app.path:
                path = path.replace(route.schema.path, '', 1)
            path = path.split("/")
            for x, part in enumerate(path):
                if not x or x > 1:
                    continue
                if part == endpoint:
                    result = _create_uri_path(route,
                                              route.path,
                                              with_hostname=with_hostname,
                                              **kwargs)
                    if result:
                        add_result(result)
        if results:
            results = sorted(results, key=lambda x: len(x[1]), reverse=True)
            if with_matches:
                return results[0]
            else:
                return results[0][0]
    return (None, []) if with_matches else None


def link_for(endpoint, text=None, appname=None, with_hostname=False,
             *args, **kwargs):
    """ Automatically generates an HTML link based on the URI endpoint
        and arguments given
        @endpoint: name of the template or the name of the
            first |/<group>/| of the URI.
        @text: #str content of the link text
        @appname: #str name of the app to look in
        @with_hostname: #bool whether or not to include a hostname with
            the URL
        @args: #str options to pass to the |a| tag
        @kwargs: named groups from the router e.g. |/users/<uid(:id)>|
            would be |link_for('users', "Username", uid=1234, rel="nofollow")|
            and key=value arguments to pass to the |a| tag,
            e.g. |rel="nofollow"|

            A keyword arg for |class| must be called |class_name|

        For additional information see :func:url_for

        ======================================================================
        ``Usage Example``
        ..
            from kola import Kola, link_for

            app1 = Kola(name="app1")
            app1.route("/u/<username([\w]+)>", View("users"), method="GET")
            app1.route("/uid/<user_id([\d]+)>", View("users"), method="GET")

            app2 = Kola(name="app2", routes=app1.routes)
            app2.route("/post/<pid(:id)>", View("posts"), method="GET")

            link_for("users", username="Bob")
            # -> <a href="/u/Bob">/u/Bob</a>

            link_for(
                "users", text="Bob", user_id=1720, with_hostname=True,
                class_name="profile-link")
            # -> <a href="http://foo.bar/uid/1720" class="profile-link">Bob</a>

            link_for(
                "users", text="Bob", username="Bob", rel="nofollow",
                data_type="profile")
            # -> <a href="/u/Bob" rel="nofollow" data-type="profile">Bob</a>

            link_for("posts", pid=1720, appname="app1")
            # -> None

            link_for(
                "posts", text="My cool post" pid=1720, appname="app2",
                class_name="posts")
            # -> <a href="/post/1720" class="posts">My cool post</a>
        ..
    """
    href, path_matches = url_for(
        endpoint, appname=appname, with_hostname=with_hostname,
        with_matches=True, **kwargs)
    options = "".join(
                " ".format(k)
                for k in args
                if k not in path_matches) + \
              "".join(
                ' {}="{}"'.format(
                    k.replace("_name", "") if k == "class_name" else
                    k.replace("_", "-"),
                    v
                )
                for k, v in kwargs.items()
                if k not in path_matches)
    return '<a href="{}"{}>{}</a>'.format(href, options, text or href)
