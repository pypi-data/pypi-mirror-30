from devconfig import module
import sys
from pprint import pprint


def test_module_finder_map_manipulates_sys_meta_path():
    module.finder['creds'] = module.credstash('credentials-table', 'eu-central-1', 'alias/alias1', app='django')
    meta_finder_type_names = [t.__name__ for t in sys.meta_path if isinstance(t, type)]
    assert '_CredstashModuleFinder' in meta_finder_type_names
    del module.finder['creds']
    meta_finder_type_names = [t.__name__ for t in sys.meta_path if isinstance(t, type)]
    assert '_CredstashModuleFinder' not in meta_finder_type_names


def test_module_finder_imports(credstash_mock):
    import credstash
    credstash.putSecret('x', '!!python/int 21', kms_key='alias/alias1', region='eu-central-1', table='test-table', context={'app':'django'})
    import creds
    assert 'x' in creds.__dict__
    assert creds.x == 21