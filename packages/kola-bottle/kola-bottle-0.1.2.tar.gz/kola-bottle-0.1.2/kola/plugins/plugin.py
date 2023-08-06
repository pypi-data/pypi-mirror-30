"""

  `Plugin base class`
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2015 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
from vital.debug import preprX


__all__ = ('Plugin',)


class Plugin(object):
    label = 'plugin'

    __repr__ = preprX('label')
