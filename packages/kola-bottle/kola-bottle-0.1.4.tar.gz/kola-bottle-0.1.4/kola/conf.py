"""

  `Kola Configuration Options`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   The MIT License (MIT) © 2015 Jared Lunde
   http://github.com/jaredlunde/VitalSQL

"""
import os
from threading import current_thread

from vital.cache import memoize, local_property
from vital.debug import preprX
from vital.tools import getitem_in

from kola.serializers import dump, load


__all__ = ('BaseConfig', 'Config', 'config')


class BaseConfig(object):
    """ A dict-like configuration object. This object sets options
        for various Kola utilities like :class:Session and
        :class:View. See the sample kola.json file for formatting.
        If no file is specified, :meth:load will check the directory
        this |kola.py| is located in.

        For builtin vital features, configurations are typically passed
        to their respective objects by unpacking the keyword via **kwargs.
        In some rare cases the object is passed via a |config={}| keyword
        argument.

        You can safely put anything you want into the configuration file as
        long as it is JSON serializable. If you require the use of python
        objects in your config, you can do this by adding them
        anywhere within your application the same way you would add to
        a python #dict.

        This instance is also locally bound to :var:config

        =======================================================================
        ``Usage Example``
        ..
            from kola import Kola, config

            # Attaches config to Kola instance
            api_handler = Kola("/path/to/kola.json")

            # Adds information to the configuration file within
            # the local thread
            api_handler.config["keyword"] = {
                "arguments": "values",
            }

            # Sets a new configuration for the api_handler
            api_handler.config.bind(your_filename)

            # Gets a key in the current thread config file
            config.get("key") or config["your_key"]

            # Iterates the current thread config file,
            # prints its keys and values
            for key, value in config.items():
                print(key, value)

            import redis
            # Redis connection example
            redis.StrictRedis(**api_handler.config["redis"])
        ..

    """
    __slots__ = ('file',)
    _bound = set()

    def __init__(self, file=None, thread=None):
        """ `Kola Config`

            @file: path/to/kola_configuration.json
        """
        self.file = file or self.file
        try:
            assert self.file in self.data
        except AssertionError:
            self.load()
        except RuntimeError:
            self.data = {}
            self.load()
        if thread:
            self._bound.add(thread)

    __repr__ = preprX('file')

    def __getitem__(self, key):
        """ Gets item from the working config
            -> value for @key
        """
        return self.data.get(self.file, {})[key]

    def __setitem__(self, key, val):
        """ Sets item from the working config """
        try:
            self.data[self.file][key] = val
        except KeyError:
            self.data[self.file] = {}
            self.data[self.file][key] = val

    def __iter__(self):
        """ -> keys of the working config """
        return self.data.get(self.file, {}).keys()

    def __len__(self):
        """ -> #len of the working config """
        return len(self.data.get(self.file, {}))

    @property
    def bound(self):
        return self.is_bound(current_thread())

    def is_bound(self, thread):
        return thread in self._bound

    def get(self, key, default=None):
        """ Gets @key from the working config

            @key: key specified in configuration file
            @default: default result to return if no key is found

            -> value or @default for @key
        """
        try:
            return self.data[self.file].get(key, default)
        except KeyError:
            return None

    def copy(self):
        """ -> copy #dict of the working configuration """
        return self.data.get(self.file, {}).copy()

    def items(self):
        """ -> (key, value) of the working configuration """
        return self.data.get(self.file, {}).items()

    def _import_deep_use(self, main_conf, conf):
        for k, v in conf.copy().items():
            if k == 'use':
                try:
                    v = getitem_in(main_conf, v)
                except KeyError:
                    v = getitem_in(conf, v)
                if isinstance(v, dict):
                    v = self._import_deep_use(main_conf, v)
                del conf['use']
                conf.update(v)
            elif isinstance(v, dict):
                v = self._import_deep_use(main_conf, v)
                conf[k] = v
        return conf

    def _import_use(self, conf):
        for k, v in conf.copy().items():
            if k == 'use':
                v = getitem_in(conf, v)
                if isinstance(v, dict):
                    v = self._import_deep_use(conf, v)
                del conf['use']
                conf.update(v)
            elif isinstance(v, dict):
                v = self._import_deep_use(conf, v)
                conf[k] = v
        return conf

    @memoize
    def _open_config(self, config_file):
        if os.path.isfile(config_file):
            conf = {}
            with open(config_file) as _conf:
                conf = self._import_use(load(_conf))
            return conf
        return {}

    def save(self, filename=None):
        """ Saves current config data to :prop:file as JSON serialized
            string
        """
        filename = filename or self.file
        if filename:
            self.save_to(filename)
        else:
            raise ValueError("Filename cannot be None.")

    def save_to(self, file):
        """ Saves config to a @file
            @file: #str /path/to/file.json
        """
        with open(config_file, "w") as _conf:
            _conf.write(dump(self.data[file], indent=2))

    def load(self, config_file=None):
        """ Loads a specified configuration file or the latest file

            -> #dict of configuration data
        """
        self.file = config_file or self.file
        if not self.file:
            basepath = os.path.dirname(__file__)
            self.file = os.path.abspath(os.path.join(basepath, "kola.json"))
        self.data[self.file] = self._open_config(self.file) or {}
        return self.data[self.file]


class Config(BaseConfig):
    file = None
    bind = BaseConfig.__init__
    data = local_property()


config = Config()
