from __future__ import absolute_import
import logging
import io
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

_log = logging.getLogger(__name__)

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
    return isinstance(obj, io.IOBase)

def iterload(*maybe_streams, populate=None):
    '''
    loads streams as yaml
    shares anchors between yamls
    yields non-stream objects as is
    '''
    Loader = shared_anchors_loader()
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
