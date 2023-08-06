[rfc2119 for keywords ](https://www.ietf.org/rfc/rfc2119.txt)

# PURPOSE
* to provide unified way to configure `python2` and `python3` application
* to be handy for developers, devops, QA and users with technical background

# READINGS
* [yaml tutorial](https://pyyaml.org/wiki/PyYAMLDocumentation#tutorial)
* http://yaml.org/spec/1.1/
* **YAML IS NOT A JSON AND NOT A DATA SERIALIZATION FORMAT. ITS A OBJECT SERIALIZATION FORMAT**

# REQUIREMENTS
 1. **MUST** support yaml out of the box
 1. **MUST** configure program (standalone module or python package) by recursive merge developer defined configuration (defaults) and runtime provided configuration.
 1. each configuration layer (e.g. defaults, runtime config, etc.) **MUST** be a nested mapping
 1. number of merged layers is unlimited and **MAY** be redefined by developer
 1. layer merge order **MAY** be redefined by developer
 1. **MUST** contain set of yaml [constructors](https://pyyaml.org/wiki/PyYAMLDocumentation#constructors-representers-resolvers)
    * `!url` 
    * `!date`
    * `!datetime` 
    * `!timedelta`
    * `!strjoin`
    * `!envvar` 
    * `!regexp`
    * `!filecontent`
 1. **SHOULD** contain set of dangerous yaml constructors
    * `!class` using [attrs](https://pypi.python.org/pypi/attrs/17.4.0)
    * `!object` factory
    * `!file`
    * `!socket`
    * `!yamlfile` - includes yaml by file path or url
 1. **MAY** process constructors with recursion detection (see REQUIREMENT NOTES)
 1. **MAY** contain cli arg mapping constructors
 1. **SHOULD** provide a way to extend set of constructors before configuration loaded
 1. **MUST** provide a way to configure logging using [`logging.dictConfig`](https://docs.python.org/3/library/logging.config.html?highlight=dictconfig) and values from merged configuration
 1. runtime configuration path **MAY** be redefined with envvar (like `$ CONFIG=./some-config.yml program.py`)
 1. runtime configuration path **MAY** be redefined with cli arg (like `$ program.py --config=./some-config.yml`)
 1. **SHOULD** enable sharing of [anchors](https://pyyaml.org/wiki/PyYAMLDocumentation#aliases) between layers
 1. **SHOULD** NOT allow to redefine anchors that alredy defined in previous layers
 1. **MUST** support filesystem path as configuration path
 1. **MUST** support `file://`, `http(s)://` urls as configuration path
 1. **MAY** support `ftp://` urls as configuration path
 1. **MAY** support `git://` urls as configuration path
 1. **SHOULD** support [`envconsul`](https://github.com/hashicorp/envconsul) as a configuration layer
 1. **SHOULD** support [`envconsul`](https://github.com/hashicorp/envconsul) as a mapping value (constructor)
 1. **SHOULD** support [`consul kv export`](https://www.consul.io/docs/commands/kv/export.html) as a configuration layer
 1. **SHOULD** support [`consul kv export`](https://www.consul.io/docs/commands/kv/export.html) as a mapping value (constructor)
 1. **SHOULD** support module as a configuration layer (for streamlined integration with existing configuration systems like `django`)

## REQUIREMENT NOTES

 * `!class`, `!object`, and `!yamlfile` are considered dangerous since class or object creation may require existing configuration that is not exists during constructor call. `!yamlfile` can refer `!class` or `!object` inside and/or cause infinte yaml load recursion or module load recursion.
 * `!file` and `!socket` are considered dangerous since they are not serializable

# IMPLEMENTATION
 * provides `<module>.<config>` submodule that contains resulting configuration as mapping


???