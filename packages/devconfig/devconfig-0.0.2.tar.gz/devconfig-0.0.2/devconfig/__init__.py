# bootstrap
import sys
import logging

from . import mapping
from . import yaml
from . import constructor

from collections import defaultdict, Mapping

class _WithList(list):
    def __init__(self, *args, **kwargs):
        self._optional = set()
        super(list, self).__init__(*args, **kwargs)

    def _with(self, *args, optional=False, clear=True):
        if clear:
            self.clear()
            self._optional.clear()
        if optional:
            self._optional.update(set(args))
        self.extend(args)

# defines merged yaml modules. Only yaml modules affected by merge
merges = defaultdict(_WithList) #noqa

# defines hooks started after module loaded. Only yaml modules affected by merge
hooks = defaultdict(_WithList) #noqa

if sys.version_info.major == 2:
    import importlib2.hook
    from importlib import import_module
    importlib2.hook.install()

    _bootstrap_module_name = 'importlib._bootstrap'

elif sys.version_info.major == 3:
    _bootstrap_module_name = 'importlib._bootstrap_external'

from importlib import import_module
_bootstrap = import_module(_bootstrap_module_name)

from importlib.abc import FileLoader
from importlib.util import find_spec
from types import ModuleType
import os.path
import logging

_log = logging.getLogger(__name__)

class YamlFileLoader(FileLoader):

    def omit_magic(self, mapping):
        return dict(((k,v) for (k,v) in mapping.items() if not k.startswith('__')))

    def get_yaml_stream(self, path):
        self.yaml_streams.append(open(path))
        _log.debug('Opened yaml stream {} from {}'.format(self.yaml_streams[-1], path))
        return self.yaml_streams[-1]

    def get_filename(self, fullname):
        return os.path.basename(fullname)

    def create_module(self, spec):
        self.yaml_streams = []
        return ModuleType(spec.name)

    def exec_module(self, module):
        merge_modules = list([module.__name__, ] + [name for name in merges[module.__name__] if not name == module.__name__])
        _log.debug('Merge modules {}'.format(merge_modules))
        mergelist = []
        for merge_module in merge_modules:
            if isinstance(merge_module, ModuleType):
                mergelist.append(self.omit_magic(merge_module.__dict__))
            elif isinstance(merge_module, Mapping):
                mergelist.append(merge_module)
            else:
                spec = find_spec(merge_module)
                if spec is None:
                    if merge_module not in merges[module.__name__]._optional:
                        raise ImportError(merge_module)
                    continue
                if isinstance(spec.loader, self.__class__):
                    mergelist.append(self.get_yaml_stream(spec.origin))
                else:
                    mergelist.append(self.omit_magic(import_module(merge_module).__dict__))
        module.__dict__.update(mapping.merge(*yaml.iterload(*mergelist, populate=constructor.populate_loader)))
        module.__merges__ = merge_modules
        module.__hook_results__ = []

        for hook in hooks[module.__name__]:
            module.__hook_results__.append(hook(module))

    def get_source(fullname):
        return 'notimplemented'

    def __del__(self):
        #buggy
        # 1. looks like loader destroyed only on program exit
        # 2. sometimes create_module not called but destructor - do
        # TODO: refactor streams management so they opened and closed in exec_module
        if hasattr(self, 'yaml_streams'):
            [stream.close() for stream in self.yaml_streams]
            _log.debug('closed streams')

import importlib

__supported_loaders = _bootstrap._get_supported_file_loaders()
__supported_loaders.append((YamlFileLoader, ['.yml', '.yaml']))
sys.path_hooks[-1] = importlib.machinery.FileFinder.path_hook(*__supported_loaders)
sys.path_importer_cache.clear()

__all__ = [ 'mapping',
            'yaml',
            'merges',
            'hooks',
            ]
