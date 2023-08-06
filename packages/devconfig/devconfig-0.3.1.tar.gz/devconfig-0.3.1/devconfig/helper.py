import sys
import re
import logging
_log = logging.getLogger(__name__)


if sys.version_info.major == 2:
    from urllib import urlencode
    from urlparse import urlsplit, urlunsplit, parse_qs, parse_qsl
else:
    from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qs, parse_qsl

NETLOC_RE = re.compile(r'(?:(?P<username>[^:]+)(?::(?P<password>.*))?@)?(?P<hostname>[^:]+)(?::(?P<port>[\d]+))?')
NETLOC_PARAMS = set(('username', 'password', 'hostname', 'port'))

NOT_PROVIDED = object()


class URL(str):
    '''
    Immutable unicode for url parsing and building
    
    ### Basestring operations
    
    ```python
    url = URL('http://den:passwd@google.com:2020/path/to?a=2&b=4%23#eee')
    assert(url == u'http://den:passwd@google.com:2020/path/to?a=2&b=4%23#eee')
    assert(url + 'ccc' == u'http://den:passwd@google.com:2020/path/to?a=2&b=4%23#eeeccc')
    ```
    ### Parsing

    ```python
    assert(url.scheme == u'https')
    assert(url.netloc == u'den:passwd@google.com:2020')
    assert(url.username == u'den')
    assert(url.password == u'passwd')
    assert(url.hostname == u'google.com')
    assert(url.port == 2020)
    assert(url.path == u'/path/to')
    assert(url.query == u'a=2&b=4%23')
    assert(url.args == {'a':['2'], 'b':['4#']})
    assert(url.fragment == 'eee')
    ```

    ### Building
    ```python
    assert(url(path='/leads/to/other/place') == u'http://den:passwd@google.com:2020/leads/to/other/place?a=2&b=4%23#eee')
    assert(url(hostname='github.com') == u'http://den:passwd@github.com:2020/leads/to/other/place?a=2&b=4%23#eee')
    ```
    
    but:

    ```python
    assert(url(netloc='github.com') == u'http://github.com/leads/to/other/place?a=2&b=4%23#eee')
    ```
    to change netloc parts - use related netloc attribute names (username, password, hostname, port) same logic with query:

    ```python
    assert(url(args={'c':22}) == u'http://github.com/leads/to/other/place?c=22#eee')
    ```    

    or:

    ```python
    assert(url(query='c=22') == u'http://github.com/leads/to/other/place?c=22#eee')
    ```    
    '''
    def __new__(cls, url=None, parsed=None):
        if parsed is not None:
            ret = str.__new__(cls, urlunsplit(parsed))
            ret._parsed = parsed
            return ret

        elif url is not None:
            return str.__new__(cls, url)

        else:
            raise TypeError('`url` or `parsed` ')

    @property
    def parsed(self):
        if getattr(self, '_parsed', None) is None:
            self._parsed = urlsplit(self)
        return self._parsed

    def __call__(self, **kwargs):
        if set(kwargs.keys()).intersection(NETLOC_PARAMS):
            username = kwargs.pop('username', NOT_PROVIDED)
            password = kwargs.pop('password', NOT_PROVIDED)
            hostname = kwargs.pop('hostname', NOT_PROVIDED)
            port = kwargs.pop('port', NOT_PROVIDED)

            def replace_netloc_parts(matchobj):

                netloc = dict(((k, v) if v is not None else '')
                                for k, v in matchobj.groupdict().items())

                def extract_part(fresh_value, old_value, prefix=None):
                    if fresh_value is NOT_PROVIDED:
                        if old_value:
                            return (prefix if prefix else '')\
                                + str(old_value)
                        else:
                            return ''
                    elif fresh_value:
                        return (prefix if prefix else '')\
                            + str(fresh_value)
                    else:
                        return ''

                ampersand = any((username,
                                password,
                                netloc['username'],
                                netloc['password']))
                return extract_part(username, netloc['username']) \
                    + extract_part(password, netloc['password'], ':') \
                    + ('@' if ampersand else '') \
                    + extract_part(hostname, netloc['hostname']) \
                    + extract_part(port, netloc['port'], ':')

            kwargs['netloc'] = re.sub(NETLOC_RE,
                                      replace_netloc_parts,
                                      self.parsed.netloc)

        if 'args' in kwargs:
            args = kwargs.pop('args')
            kwargs['query'] = urlencode(args if args else {})

        for name, value in kwargs.items():
            if value is None:
                kwargs[name] = ''

        return URL(parsed=self.parsed._replace(**kwargs))

    def __getattr__(self, name):
        if name in ('_parsed', '_args'):
            return None

        return getattr(self.parsed, name)

    @property
    def args(self):
        '''build and cache `args` dict'''
        if not getattr(self, '_args', None):
            self._args = parse_qs(self.query)

        return self._args

    def update_args(self, *args, **kwargs):
        '''
        rebuild query and return new URL

        ```python
        assert(url.update_args(c=22) == u'http://github.com/leads/to/other/place??a=2&b=4%23&c=22#eee')
        ```
        or 

        ```python
        assert(url.update_args(('c', 22), d=33) == u'http://github.com/leads/to/other/place??a=2&b=4%23&c=22&e=33#eee')
        ```
        
        '''
        current = dict(((k, (v[0] if len(v) == 1 else v))
                        for k, v in parse_qsl(self.query)))
        current.update(dict(args))
        current.update(kwargs)
        return URL(parsed=self.parsed._replace(query=urlencode(current)))

    def sub(self, subpath, **kwargs):
        '''
        Add subpath to existing url

        ```python
        url = URL('http://den:passwd@google.com:2020/path/to?a=2&b=4%23#eee')
        assert(url.sub('something') == 'http://den:passwd@google.com:2020/path/to/something?a=2&b=4%23#eee')
        ```
        '''
        kwargs.pop('path', None)
        return self(path='/'.join((self.path.rstrip('/'), subpath)), **kwargs)


import io
import types
from copy import copy
from pprint import pformat
import yaml

from yaml.reader import Reader
from yaml.scanner import Scanner
from yaml.parser import Parser
from yaml.composer import Composer
from yaml.constructor import Constructor
from yaml.resolver import Resolver
from yaml.loader import Loader


if sys.version_info.major == 2:
    STREAM_TYPES = (io.TextIOBase, types.FileType)
else:
    STREAM_TYPES = (io.TextIOBase,)


def shared_anchors_loader(anchors=None):
    _anchors = copy(anchors) if anchors else {}

    class SharedAnchorsComposer(Composer):
        def __init__(self):
            self.anchors = _anchors

    class SharedAnchorsLoader(Reader, Scanner, Parser, SharedAnchorsComposer, Constructor, Resolver):
        def __init__(self, stream):
            Reader.__init__(self, stream)
            Scanner.__init__(self)
            Parser.__init__(self)
            SharedAnchorsComposer.__init__(self)
            Constructor.__init__(self)
            Resolver.__init__(self)

    SharedAnchorsLoader._anchors = _anchors

    return SharedAnchorsLoader

def is_stream(obj):
    return isinstance(obj, STREAM_TYPES)

def iterload(*maybe_streams, **kwargs):
    '''
    loads streams as yaml
    shares anchors between yamls
    yields non-stream objects as is
    '''
    Loader = shared_anchors_loader()
    populate = kwargs.get('populate', None)
    if populate:
        populate(Loader)
    _log.debug('new shared loader 0x{:02X}'.format(id(Loader)))
    for maybe_stream in maybe_streams:
        if is_stream(maybe_stream):
            _log.debug('Yielding yaml stream {}. Loader 0x{:02X}. Anchors {} '.format(maybe_stream, id(Loader), Loader._anchors))
            mapping = yaml.load(maybe_stream, Loader=Loader)
            yield mapping if mapping is not None else {}
        else:
            _log.debug('Yielding object {} with loader 0x{:02X}'.format(maybe_stream, id(Loader)))
            yield maybe_stream

