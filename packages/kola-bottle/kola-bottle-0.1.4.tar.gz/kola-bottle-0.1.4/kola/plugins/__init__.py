#!/usr/bin/python3 -S
"""

 `Kola Plugins`
  Useful plugins to add to your kola instances

  ===========================
  ``Create your own plugins``

  Plugins are executed in the order which they are added to a
  :class:kola.Kola instance.

  The only requirement for creating plugins is that they are #callable and
  accept one argument in the apply method for the :class:kola.Route instance
  which the plugin is installed to.

  Plugins with an |apply| method will perform slightly better than callable
  ones.

  =========================
  ```Required Attributes```
  - |label| is the name of the plugin which can be used to ignore certain
    plugins on :class:kola.Route(s)

  ```Optional Methods```
  - |setup| is executed when the route the plugin belongs to is installed.
  - |apply| is executed before the route callback is executed.
  - |close| is executed after the route callback has been executed.
  - |copy| is for customized copy behavior. Plugins are copied for each
    :class:kola.Route instance. If no |copy| is specified, the default
    behavior will be used

  ===========
  ```Usage```
  ..
    from kola.plugins import Plugin

    class YourPlugin(Plugin):
        label="my_plugin"

        def apply(self, route):
            pass

        def close(self):
            pass

        def copy(self):
            return self.__class__()

    your_kola.install(YourPlugin())
  ..

--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2016 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
from kola.plugins.plugin import *
from kola.plugins.auth import *
from kola.plugins.cache import *
from kola.plugins.csrf import *
from kola.plugins.sessions import *
from kola.plugins.runtime import *
