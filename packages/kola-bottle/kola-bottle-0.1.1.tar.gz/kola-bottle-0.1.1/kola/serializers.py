try:
    from ujson import dumps as _dumps, loads, load, dump as _dump
except:
    from json import dumps as _dumps, loads, load, dump as _dump

from vital.tools import strings as string_tools
from vital.tools import html as html_tools


__all__ = ('dumps', 'loads', 'load', 'dump')


#
#  ``JSON dumper``
#
def dumps(x, *args, bigint_as_string=False, js_escape=False, **kwargs):
    """ Converts big integers to strings via a hacky regex approach
        because of this: https://github.com/esnme/ultrajson/issues/182

        @x: the object to json dump
        @bigint_as_string: (#bool) True if you wish to convert big integers
            to strings using :func:vital.tools.strings.json_bigint_to_string,
            defaults to |True|
        @js_escape: (#bool) |True| to serialize the object for embedding in
            javascript e.g. |var User = "{\\"hello\\": \\"world\\\\n\\"}|
        @*args: arguments to pass to :func:ujson.dumps
        @**kwargs: keyword arguments to pass to :func:ujson.dumps
        -> JSON encoded #str

        Configurable via :var:config e.g.
        ..
            "autojson": {
                "bigint_as_string": false,
                "encode_html_chars": true
            }
        ..
    """
    dumped = _dumps(x, *args, **kwargs)
    if bigint_as_string is True:
        dumped = string_tools.json_bigint_to_string(dumped)
    if js_escape is True:
        dumped = _dumps(dumped)
    return dumped


def dump(x, *args, bigint_as_string=None, **kwargs):
    """ Converts big integers to files via a hacky regex approach
        because of this: https://github.com/esnme/ultrajson/issues/182

        @x: the object to json dump
        @bigint_as_string: #bool True if you wish to convert big integers
            to strings using :func:vital.tools.strings.json_bigint_to_string,
            defaults to |True|
        @*args: arguments to pass to :func:ujson.dumps
        @**kwargs: keyword arguments to pass to :func:ujson.dumps
        -> JSON encoded #str

        Configurable via :var:config e.g.
        ..
            "autojson": {
                "bigint_as_string": false,
                "encode_html_chars": true
            }
        ..
    """
    dumped = _dump(x, *args, **kwargs)
    if escape is True:
        dumped = string_tools.escape_json(dumped)
    if bigint_as_string:
        return string_tools.json_bigint_to_string(dumped)
    else:
        return  dumped
