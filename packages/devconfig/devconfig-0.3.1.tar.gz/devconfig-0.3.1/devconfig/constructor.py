import io
import os
import sys
import locale
import pkg_resources as pkg
from datetime import timedelta
import itertools
from re import compile as re_compile
from collections import Mapping, Iterable
from functools import partial
import argparse

from devconfig.helper import URL

import yaml.nodes
import yaml.constructor

if sys.version_info.major == 3:
    basestring = str

class ConfigurationError(ValueError):
    """ Configuration error"""

def obj_constructor(loader, node):
    '''object importer

config:
```
timezone: obj! pytz.utc
```
usage in code:
```
assert config['timezone'] == pytz.utc
```
    '''
    return import_string(loader.construct_scalar(node))


def url_constructor(loader, node):
    '''URL constructor

config:
```
addr: url! http://user:pass@www.google.com:332/sub1?a=2
```
usage in code:
```
assert config['addr'](path='anothersub') == 'http://user:pass@www.google.com:332/anothersub?a=2'
```
    '''

    return URL(loader.construct_scalar(node))


def timedelta_constructor(loader, node):
    '''Timedelta constructor

config:
```
wait: timedelta! 2h
```
usage in code:
```
from datetime import timedelta
assert config['wait'] == timedelta(hours=2)
```

> available codes: d, h, w, m, s
    '''

    item = loader.construct_scalar(node)

    if not isinstance(item, basestring) or not item:
        raise ConfigurationError(
            "value '%s' cannot be interpreted as date range" % item)
    num, typ = item[:-1], item[-1].lower()

    if not num.isdigit():
        raise ConfigurationError(
            "value '%s' cannot be interpreted as date range" % item)

    num = int(num)

    if typ == "d":
        return timedelta(days=num)
    elif typ == "h":
        return timedelta(seconds=num * 3600)
    elif typ == "w":
        return timedelta(days=num * 7)
    elif typ == "m":
        return timedelta(seconds=num * 60)
    elif typ == "s":
        return timedelta(seconds=num)
    else:
        raise ConfigurationError(
            "value '%s' cannot be interpreted as date range" % item)


def re_constructor(loader, node):
    '''Timedelta constructor

config:
```
allchars: !re .*
```
usage in code:
```
from datetime import timedelta
assert config['allchars'].match('asdfg')
```
    '''
    item = loader.construct_scalar(node)

    if not isinstance(item, basestring) or not item:
        raise ConfigurationError(
            "value '%s' cannot be interpreted as regular expression" % item)

    return re_compile(item)


def directory_constructor(loader, node):
    '''Directory constructor

config:
```
etc: !dir /tmp/etc
```
usage in code:
```
import os
assert os.path.exists(config['etc'])
```
> creates directory if not exists. Raises if path exists and not directory
    '''

    item = loader.construct_scalar(node)
    if not os.path.exists(item):
        os.mkdir(item)
    elif not os.path.isdir(item):
        raise ConfigurationError("'%s' is not a directory" % item)
    return item

DEFAULT_DELIMITER = ''
DEFAULT_FILE_ENCODING = locale.getpreferredencoding(False)



def strjoin_constructor_mapping(loader, nodes, default_delimiter=DEFAULT_DELIMITER):
    joined = []
    for node in nodes.value:
        if isinstance(node[1], yaml.nodes.SequenceNode):
            joined.extend(loader.construct_sequence(node[1]))

    delimiter = loader.construct_mapping(nodes).get('delimiter', default_delimiter)
    return delimiter.join(str(i) for i in joined)

def strjoin_constructor_sequence(loader, items, delimiter, default_delimiter=DEFAULT_DELIMITER):
    if not delimiter:
        delimiter = default_delimiter
    elif delimiter == ':':
        delimiter = ' '
    else:
        delimiter = delimiter[1:] if delimiter[0] == ':' else delimiter
    items = loader.construct_sequence(items)
    return str(delimiter).join(str(i) for i in items)

def strjoin_constructor(loader, delimiter, node):
    if isinstance(node, yaml.nodes.SequenceNode):
        return strjoin_constructor_sequence(loader, node, delimiter)
    elif isinstance(node, yaml.nodes.MappingNode):
        return strjoin_constructor_mapping(loader, node)
    raise yaml.constructor.ConstructorError('attempt to !strjoin on node with unknown layout')


def flatten_list_constructor(loader, delimiter, node):
    return list(itertools.chain(*[loader.construct_sequence(item) for item in node.value]))

def envvar_constructor(loader, delimiter, node, nonexistent=object()):
    varname = delimiter[delimiter.index(':') + 1:]
    if isinstance(node, yaml.nodes.MappingNode):
        envvar_config = loader.construct_mapping(node)
    elif isinstance(node, yaml.nodes.ScalarNode):
        envvar_config = {}
    else:
        raise yaml.constructor.ConstructorError('!envvar format is not supported')

    construct = partial(envvar_config.get('constructor', lambda x:x))
    if 'default' in envvar_config:
        return construct(os.environ.get(varname, envvar_config['default']))
    else:
        return construct(os.environ[varname])

def file_contents_constructor(loader, coding, node, default_coding=DEFAULT_FILE_ENCODING):
    if not coding or coding==':':
        coding = default_coding
    else:
        coding = coding[1:] if coding[0] == ':' else coding

    with io.open(loader.construct_scalar(node), encoding=coding) as file_contents:
        return file_contents.read()


def cliarg_constructor(loader, delimiter, node):
    '''
    parse single cli arg with 'parse_known_args'
    '''
    cliarg_name_or_flags = delimiter[delimiter.index(':') + 1:]
    cliarg_name_or_flags = cliarg_name_or_flags.split(':')
    if isinstance(node, yaml.nodes.MappingNode):
        add_argument_kwargs = loader.construct_mapping(node)
    elif isinstance(node, yaml.nodes.ScalarNode):
        add_argument_kwargs = {}
    else:
        raise yaml.constructor.ConstructorError('!cliarg format is not supported')

    parser_kwargs = add_argument_kwargs.pop('parser', {})
    parser = argparse.ArgumentParser(**parser_kwargs)
    arg = parser.add_argument(*cliarg_name_or_flags, **add_argument_kwargs)
    return getattr(parser.parse_known_args(sys.argv)[0], arg.dest)

SCALARS = {'!obj': obj_constructor,
           '!url': url_constructor,
           '!timedelta': timedelta_constructor,
           '!re': re_constructor,
           '!dir': directory_constructor,
          }
MULTIS = {'!strjoin': strjoin_constructor,
          '!file_contents': file_contents_constructor,
          '!envvar': envvar_constructor,
          '!cliarg': cliarg_constructor,
          '!flatten': flatten_list_constructor,
          }


def populate_loader(loader):
    """populate `loader` with constructors
    """
    for tag, constructor in MULTIS.items():
        loader.add_multi_constructor(tag, constructor)

    for tag, constructor in SCALARS.items():
        loader.add_constructor(tag, constructor)
