from .patch_moto import patch_moto_kms

import devconfig
from devconfig import module
import credstash
import sys
import pytest
import yaml
import moto
import boto3
from collections import namedtuple
from xml.sax import xmlreader

tested_loggers = ['devconfig',]

# FIX: devconfig-pytest breaks pytest-logs and pytest-coverage
# def pytest_logger_config(logger_config):
#     logger_config.add_loggers(tested_loggers, stdout_level='debug')
#     logger_config.set_log_option_default(','.join(tested_loggers))
REGION = 'eu-central-1'
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

AWSConnection = namedtuple('AWSConnection', ('client', 'resource'))

@pytest.yield_fixture(scope="function")
def kms():
    patch_moto_kms()
    mock = moto.mock_kms()
    mock.start()
    kms = boto3.client('kms', region_name='eu-central-1')
    key_resp = kms.create_key()
    key_id = key_resp['KeyMetadata']['KeyId']
    kms.create_alias(AliasName='alias/alias1', TargetKeyId=key_id)
    yield AWSConnection(client = kms, resource = None)
    mock.stop()

@pytest.yield_fixture(scope="function")
def dynamodb():
    moto.mock_dynamodb2().start()
    yield AWSConnection(client = boto3.client("dynamodb", region_name=REGION), resource = boto3.resource("dynamodb", region_name=REGION))
    moto.mock_dynamodb2().stop()


CredstashMock = namedtuple('CredstashMock', ('kms', 'dynamodb', 'region'))
@pytest.yield_fixture(scope="function")
def credstash_mock(kms, dynamodb):
    module.finder['creds'] = module.credstash('test-table', 'eu-central-1', 'alias/alias1', app='django')

    sys.argv = ['credstash', '-r', REGION, '-t', 'test-table', 'setup']
    credstash.main()
    yield CredstashMock(kms=kms, dynamodb=dynamodb, region=REGION)
