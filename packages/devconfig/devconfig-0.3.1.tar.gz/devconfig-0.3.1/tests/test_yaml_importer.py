import os
import sys


def test_importer_finds_yaml_file_along_with_py_files():
    from tests.samples import empty
    assert empty.__file__ == os.path.abspath('tests/samples/empty.yaml')


def test_py_file_has_priority_over_yaml_in_same_path():
    from tests.samples import yaml_not_imported
    assert yaml_not_imported.__file__ == os.path.abspath('tests/samples/yaml_not_imported.py')


def test_pythonpath_determines_yaml_modules_search():
    sys.path.append(os.path.abspath('tests/samples/pythonpath_test'))
    import non_init_module