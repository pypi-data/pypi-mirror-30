import pytest
import yaml

tested_loggers = ['devconfig',]

def pytest_logger_config(logger_config):
    logger_config.add_loggers(tested_loggers, stdout_level='debug')
    logger_config.set_log_option_default(','.join(tested_loggers))

@pytest.yield_fixture
def mocked_iterload(mocker):
    _load = yaml.load
    yaml.load = mocker.Mock()
    yield yaml.load 
    yaml.load = _load

@pytest.yield_fixture
def empty_yaml_open_file():
    with open('tests/samples/empty.yaml', 'r') as empty_yaml:
        yield empty_yaml
