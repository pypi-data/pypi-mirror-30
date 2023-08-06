import sys
import logging
from collections import Mapping

if sys.version_info.major == 3:
    from collections import ChainMap
else:
    from chainmap import ChainMap

_log = logging.getLogger(__name__)

class NestedChainMap(ChainMap):
    def __getitem__(self, name):
        value = super(self.__class__, self).__getitem__(name)
        if isinstance(value, self.__class__):
            return value

        contexts = [m.get(name) for m in self.maps if name in m]

        if all((isinstance(ctx, Mapping) for ctx in contexts)):
            return self.__class__(*contexts)
        elif isinstance(contexts[0], Mapping):
            return self.__class__(*(c for c in contexts if isinstance(c, Mapping)))
        else:
            return contexts[0]

    def as_dict(self):
        return dict((k,(v.as_dict() if isinstance(v, self.__class__) else v)) for k,v in self.items())


def merge(*mappings):
    '''
    Merges `*mappings` list with priority to last item
    '''
    _log.debug('{!r}'.format(mappings))
    return NestedChainMap(*(mappings)).as_dict()