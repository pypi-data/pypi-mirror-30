from __future__ import absolute_import

import importlib.abc
from importlib.machinery import ModuleSpec
import logging
import types
import sys
import io
import json
from functools import partial
from devconfig.helper import URL, iterload
from devconfig import constructor
from devconfig import mapping

from credstash import getAllSecrets
import yaml

if sys.version_info.major == 3:
    unicode = str

_log = logging.getLogger(__name__)

def url_args_dict(args):
    args_dict = {}
    for k,v in args.items():
        args_dict[k] = v[0] if len(v) == 1 else v
    return args_dict

class CredstashModuleLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return types.ModuleType(spec.name)

    def exec_module(self, module):
        origin = module.__spec__.origin
        _log.debug('Loading all secrets from {} into module {}'.format(origin, module))

        secrets = []
        for name, value in getAllSecrets(region=origin.hostname,
                                table=origin.path,
                                context=url_args_dict(origin.args),
                                ).items():
            _log.debug('{}'.format(name), extra=value)
            secrets.append(io.StringIO(unicode('{}: {}'.format(name, value))))
        module.__dict__.update(mapping.merge(*iterload(*secrets, populate=constructor.populate_loader)))


def CredstashModuleFinder(table, region, key_id, module_name, **context):
    if region is None:
        region = 'default-region'
    class _CredstashModuleFinder(importlib.abc.MetaPathFinder):
        @classmethod
        def find_spec(cls, fullname, path, target=None):
            if fullname != module_name:
                return
            module_url = URL('credstash://{}'.format(region))
            return ModuleSpec(fullname, CredstashModuleLoader(), origin=module_url(args=context, path=table, fragment=key_id))


    return _CredstashModuleFinder

def credstash_finder_memoize(dynamodb_table, region, key_id, **context):
    return partial(CredstashModuleFinder, dynamodb_table, region, key_id, **context)