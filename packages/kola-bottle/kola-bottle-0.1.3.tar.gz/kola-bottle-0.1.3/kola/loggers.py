from vital.debug import Logg
from vital.cache import local_property

from kola.conf import config


__all__ = ('logg',)


#
# ``Logging``
#
_logg = local_property()
_logg = Logg()


def logg(*args, **kwargs):
    """ Thin wrapper for :class:vital.debug.Logg
        Sets the log level specified in the active configuration,
        then returns :var:_logg instance.

        Acts the same way :class:vital.debug.Logg does

        Configurable with kola.json, passes the key/value pairs from the
        config as keyword arguments to :class:vital.debug.Logg
        ..
            "logg": {
                "loglevel": "n",
                "pretty": false,
                "include_time": true
            }
        ..
    """
    try:
        logg_kwargs = {k: v for k, v in config.get('logg', {}).items()}
        logg_kwargs.update(kwargs)
        return _logg(*args, **logg_kwargs)
    except RuntimeError:
        return _logg(*args, **kwargs)
