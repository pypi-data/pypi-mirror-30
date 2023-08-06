<h1 id="devconfig">devconfig</h1>


<h1 id="devconfig.mapping">devconfig.mapping</h1>


<h2 id="devconfig.mapping.merge">merge</h2>

```python
merge(*mappings)
```

Merges `*mappings` list with priority to last item

<h1 id="devconfig.yaml">devconfig.yaml</h1>


<h2 id="devconfig.yaml.iterload">iterload</h2>

```python
iterload(*maybe_streams, populate=None)
```

loads streams as yaml
shares anchors between yamls
yields non-stream objects as is

<h1 id="devconfig.constructor">devconfig.constructor</h1>


<h2 id="devconfig.constructor.ConfigurationError">ConfigurationError</h2>

```python
ConfigurationError(self, /, *args, **kwargs)
```
Configuration error
<h2 id="devconfig.constructor.obj_constructor">obj_constructor</h2>

```python
obj_constructor(loader, node)
```
object importer

config:
```
timezone: obj! pytz.utc
```
usage in code:
```
assert config['timezone'] == pytz.utc
```

<h2 id="devconfig.constructor.url_constructor">url_constructor</h2>

```python
url_constructor(loader, node)
```
URL constructor

config:
```
addr: url! http://user:pass@www.google.com:332/sub1?a=2
```
usage in code:
```
assert config['addr'](path='anothersub') == 'http://user:pass@www.google.com:332/anothersub?a=2'
```

<h2 id="devconfig.constructor.timedelta_constructor">timedelta_constructor</h2>

```python
timedelta_constructor(loader, node)
```
Timedelta constructor

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

<h2 id="devconfig.constructor.re_constructor">re_constructor</h2>

```python
re_constructor(loader, node)
```
Timedelta constructor

config:
```
allchars: !re .*
```
usage in code:
```
from datetime import timedelta
assert config['allchars'].match('asdfg')
```

<h2 id="devconfig.constructor.directory_constructor">directory_constructor</h2>

```python
directory_constructor(loader, node)
```
Directory constructor

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

<h2 id="devconfig.constructor.cliarg_constructor">cliarg_constructor</h2>

```python
cliarg_constructor(loader, delimiter, node)
```

parse single cli arg with 'parse_known_args'

<h2 id="devconfig.constructor.populate_loader">populate_loader</h2>

```python
populate_loader(loader)
```
populate `loader` with constructors

<h1 id="devconfig.helper">devconfig.helper</h1>


<h2 id="devconfig.helper.URL">URL</h2>

```python
URL(self, /, *args, **kwargs)
```

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

<h3 id="devconfig.helper.URL.args">args</h3>

build and cache `args` dict
<h3 id="devconfig.helper.URL.update_args">update_args</h3>

```python
URL.update_args(self, *args, **kwargs)
```

rebuild query and return new URL

```python
assert(url.update_args(c=22) == u'http://github.com/leads/to/other/place??a=2&b=4%23&c=22#eee')
```
or

```python
assert(url.update_args(('c', 22), d=33) == u'http://github.com/leads/to/other/place??a=2&b=4%23&c=22&e=33#eee')
```


<h3 id="devconfig.helper.URL.sub">sub</h3>

```python
URL.sub(self, subpath, **kwargs)
```

Add subpath to existing url

```python
url = URL('http://den:passwd@google.com:2020/path/to?a=2&b=4%23#eee')
assert(url.sub('something') == 'http://den:passwd@google.com:2020/path/to/something?a=2&b=4%23#eee')
```

