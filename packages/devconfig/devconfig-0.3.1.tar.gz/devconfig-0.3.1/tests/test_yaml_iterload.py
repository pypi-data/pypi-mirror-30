import io
import sys
import yaml
import logging

from devconfig.helper import iterload
if sys.version_info.major == 2:
    str = unicode
def test_iterload_detects_and_loads_single_stream(mocked_iterload, empty_yaml_open_file):
    stream = empty_yaml_open_file
    list(iterload(stream))
    yaml.load.assert_called_once()


def test_iterload_not_detects_non_stream(mocked_iterload):
    stream = {}
    list(iterload(stream))
    yaml.load.assert_not_called()


def test_iterload_omits_non_stream(mocked_iterload, empty_yaml_open_file):
    stream0 = {}
    stream1 = empty_yaml_open_file
    assert list(iterload(stream0, stream1))[0] is stream0
    assert yaml.load.call_args[0][0] is stream1


def test_iterload_shares_anchors():
    yaml1 = io.StringIO(u'x: &xxx 1')
    yaml2 = io.StringIO(u'---\ny: 2\nz: *xxx')
    assert list(iterload(yaml1, yaml2)) == [{'x': 1}, {'y': 2, 'z': 1}]


def test_iterload_shares_anchors_with_intermediate_dict():
    yaml1 = io.StringIO(u'x: &xxx 1')
    yaml2 = io.StringIO(u'---\ny: 2\nz: *xxx')
    assert list(iterload(yaml1, {'a': 0}, yaml2)) == [{'x': 1}, {'a':0}, {'y': 2, 'z': 1}]