# bootstrap
import sys
if sys.version_info.major == 2:
    import importlib2.hook
    importlib2.hook.install()
    _bootstrap_module_name = 'importlib2._bootstrap'

elif sys.version_info.major == 3:
    _bootstrap_module_name = 'importlib._bootstrap_external'

from importlib.abc import FileLoader #noqa

class YamlFileLoader(FileLoader):

    def omit_magic(self, mapping):
        return dict(((k,v) for (k,v) in mapping.items() if not k.startswith('__')), __builtins__={})

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
        if 'of_config' in globals().keys() and of_config:
            if module.__name__ in of_config.merges.keys():
                merges[module.__name__] = of_config.merges[module.__name__]['with']

        merge_modules = list([module.__name__, ] + [name for name in merges[module.__name__] if not name == module.__name__])
        _log.info('Merge modules {}'.format(merge_modules))
        mergelist = []
        for merge_module in merge_modules:
            if isinstance(merge_module, ModuleType):
                mergelist.append(self.omit_magic(merge_module.__dict__))
            elif isinstance(merge_module, Mapping):
                mergelist.append(merge_module)
            else:
                spec = find_spec(merge_module)
                if spec is None:
                    if merge_module not in getattr(merges[module.__name__], '_optional', set()):
                        raise ImportError(merge_module)
                    continue
                if isinstance(spec.loader, self.__class__):
                    mergelist.append(self.get_yaml_stream(spec.origin))
                else:
                    mergelist.append(self.omit_magic(import_module(merge_module).__dict__))

        module.__pre_hook_results__ = []


        for hook in hooks[module.__name__]._before_module_exec:
            module.__pre_hook_results__.append(hook(module, mergelist))
            _log.debug('Pre-hook {} executed at {} with result {}'.format(hook, module, module.__pre_hook_results__[-1]))

        mergelist.append(module.__dict__)
        module.__dict__.update(mapping.merge(*reversed(list(helper.iterload(*reversed(mergelist), populate=constructor.populate_loader)))))
        module.__merges__ = merge_modules

        module.__post_hook_results__ = []
        for hook in hooks[module.__name__]._after_module_exec:
            module.__post_hook_results__.append(hook(module, mergelist))
            _log.debug('Post-hook {} executed at {} with result {}'.format(hook, module, module.__post_hook_results__[-1]))

    def get_source(fullname):
        return 'notimplemented'

    def __del__(self):
        #buggy
        # 1. looks like loader destroyed only on program exit
        # 2. sometimes create_module not called but destructor - do
        # TODO: refactor streams management so they opened and closed in exec_module
        if hasattr(self, 'yaml_streams'):
            [stream.close() for stream in self.yaml_streams]



from importlib import import_module #noqa
import importlib.machinery #noqa

_bootstrap = import_module(_bootstrap_module_name) #noqa
__supported_loaders = _bootstrap._get_supported_file_loaders() #noqa
__supported_loaders.append((YamlFileLoader, ['.yml', '.yaml'])) #noqa
sys.path_hooks[-1] = importlib.machinery.FileFinder.path_hook(*__supported_loaders) #noqa
sys.path_importer_cache.clear() #noqa


from collections import defaultdict, Mapping #noqa
import attr

class _WithList(list):
    def __init__(self, *args, **kwargs):
        self._optional = set()
        super(list, self).__init__(*args, **kwargs)

    def _with(self, *args, **kwargs):
        optional = kwargs.get('optional', False)
        clear = kwargs.get('clear', True)
        if clear:
            self.clear()
            self._optional.clear()
        if optional:
            self._optional.update(set(args))
        self.extend(args)

    if sys.version_info.major == 2:
        def clear(self):
            for i in range(len(self)):
                self.pop()

# defines merged yaml modules. Only yaml modules affected by merge
merges = defaultdict(_WithList) #noqa

def get_module_hooks_class():
    import attr
    def get_list_method(list_name):
        def _list_method(self, *args, **kwargs):
            clear = kwargs.get('clear', True)
            hook_list = getattr(self, '_{}_module_exec'.format(list_name))
            if clear:
                getattr(self, 'clear_{}_module_exec'.format(list_name))()

            hook_list.extend(args)
        return _list_method

    def get_list_clear_method(list_name):
        def _list_clear_method(self):
            hook_list = getattr(self, '_{}_module_exec'.format(list_name))
            for i in range(len(hook_list)):
                hook_list.pop()
        return _list_clear_method

    @attr.s
    class _ModuleHooks(object):
        for _LIST_NAME in ('before', 'after'):
            locals()['_{}_module_exec'.format(_LIST_NAME)] = attr.ib(default=attr.Factory(list))
            locals()['{}_module_exec'.format(_LIST_NAME)] = get_list_method(_LIST_NAME)
            locals()['clear_{}_module_exec'.format(_LIST_NAME)] = get_list_clear_method(_LIST_NAME)

        del locals()['_LIST_NAME']

    return _ModuleHooks

# defines hooks started before and after module executed. Only yaml modules affected by merge
hooks = defaultdict(get_module_hooks_class()) #noqa

import logging
_log = logging.getLogger(__name__) #noqa

import os

CONFIG_OF_CONFIG_MODULE_NAME = os.environ.get('config_of_config', 'config_of_config')
merges[CONFIG_OF_CONFIG_MODULE_NAME]._with('devconfig.defaults')



from types import ModuleType #noqa
import os.path #noqa

from importlib.util import find_spec #noqa
from importlib import import_module


from . import helper #noqa
from . import mapping #noqa
from . import constructor #noqa
from . import module
__all__ = [ 'mapping',
            'yaml',
            'merges',
            'hooks',
            'helper',
            'constructor'
            ]
try:
    of_config = import_module(CONFIG_OF_CONFIG_MODULE_NAME)
    for module_name, finder in getattr(of_config, 'module', {}).get('finders', {}).items():
        _log.debug('Create finder {} for module {}'.format(finder, module_name))
        module.finder[module_name] = getattr(module, finder['finder'])(*finder['args'], **finder['kwargs'])

    if 'module_name' in locals():
        del locals()['module_name']
    if 'finder' in locals():
        del locals()['finder']

    if hasattr(of_config, 'logging'):
        import logging.config
        logging.config.dictConfig(of_config.logging)
except ImportError:
    of_config = None

