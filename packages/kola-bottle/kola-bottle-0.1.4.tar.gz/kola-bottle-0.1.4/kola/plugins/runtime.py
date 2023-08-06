"""

  `App Runtime Plugin`
   Keep track of how long your callbacks and plugins take to execute,
   via useful statistics.
--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--·--
   2016 Jared Lunde © The MIT License (MIT)
   http://github.com/jaredlunde

"""
from vital.debug import Timer, preprX

from kola.requests import request as request_
from kola.responses import response as response_
from kola.plugins import Plugin


def to_msecs(t):
    return t * 1000


def to_string(name, value, description):
    return '%s;dur=%s%s' % (
        name,
        to_msecs(value),
        f';desc="{description}"' if description is not None else ''
    )

DESCRIPTIONS = {
    'latest': 'Response time',
    'mean': 'Server mean',
    'max': 'Server max',
    'min': 'Server min',
    'stdev': 'Server stdev'
}


__all__ = ('AppRuntime',)

class AppRuntime(Timer, Plugin):
    """ =================
        ``Usage Example``
        ..
            from kola import Kola
            from kola.plugins import AppRuntime

            rt = AppRuntime(precision=4, output=['latest', 'median'])

            cool_app = Kola()
            cool_app.install(rt)
        ..
    """
    label = 'server_timing'

    def __init__(
        self,
        *args,
        name=None,
        precision=5,
        output=None,
        request=None,
        response=None,
        **kwargs
    ):
        """ `App Runtime Plugin`

            This plugin sets a header in your WSGI response which indicates
            statistics for selected @output attributes. An @output set
            to |['latest', 'max', 'median']| might set the header value
            to |latest=0.02351; max=0.68023; median=0.13222;|

            This plugin should only be used for debugging purposes, although
            the interval data is stored in a quick and memory-efficient
            way using :class:Timer.

            @*args: arguments to pass to :class:Timer
            @name: (#str) name of the header to set
            @output: (#list) of :class:Timer attribute names
                (e.g. |['latest', 'median']|) in the header
            @**kwargs: keyword arguments to pass to :class:Timer

        """
        super().__init__(*args, _precision=precision, **kwargs)
        self.name = name or 'Server-Timing'
        self.request = request or request_
        self.response = response or response_
        self.timers = {}
        self.metrics = []

    __repr__ = preprX('label', 'output', keyless=True, address=False)

    def apply(self, route):
        setattr(self.request, self.label, self.__class__(name=self.name))
        self.request_timer.start()

    @property
    def request_timer(self):
        return getattr(self.request, self.label)

    @property
    def total_response_time(self):
        return to_string('total', self.request_timer.exectime, 'Response time')

    def set_metric(self, name, value, description=None):
        self.request_timer.metrics.append(
            to_string(name, value, description)
        )

    def start_metric(self, name, description=None):
        self.request_timer.timers[name] = {
            'timer': Timer(),
            'description': description
        }
        self.request_timer.timers[name]['timer'].start()

    def stop_metric(self, name):
        timer = self.request_timer.timers[name]
        timer['timer'].stop()
        self.request_timer.set_metric(
            name,
            timer['timer'].exectime,
            timer['description']
        )

    def close(self):
        self.request_timer.stop()

        if len(self.request_timer.metrics):
            timings = f"{','.join(self.request_timer.metrics)},{self.request_timer.total_response_time}"
        else:
            timings = self.request_timer.total_response_time

        self.response.set_header(self.request_timer.name, timings)
