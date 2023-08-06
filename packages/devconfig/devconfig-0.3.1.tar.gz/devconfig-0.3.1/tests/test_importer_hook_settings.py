import devconfig
import sys
import importlib

def test_yaml_module_after_module_exec_hook():
    devconfig.hooks['tests.samples.merged4'].after_module_exec(lambda module, mergelist: module.hookdict.update({'b': module.hookdict['a'] + 3}))
    from tests.samples import merged4
    assert merged4.hookdict == {'a': 1, 'b': 4}

def test_yaml_module_before_module_exec_hook():
    devconfig.hooks['tests.samples.merged8'].before_module_exec(lambda module, mergelist: module.__dict__.update({'hookdict':{'c':2}}))
    devconfig.hooks['tests.samples.merged8'].after_module_exec(lambda module, mergelist: module.hookdict.update({'b': module.hookdict['a'] + module.hookdict['c']}))
    from tests.samples import merged8
    assert merged8.hookdict == {'a': 1, 'b': 3, 'c': 2}

def test_yaml_module_intermediate_hook():
    devconfig.merges['tests.samples.merged6']._with('tests.samples.merged5')
    devconfig.hooks['tests.samples.merged6'].after_module_exec(lambda module, mergelist: module.hookdict.update({'b': 2}))
    from tests.samples import merged6
    devconfig.merges['tests.samples.merged7']._with(merged6)

    from tests.samples import merged7
    assert merged7.hookdict == {'a':1, 'b': 2, 'c': 3, 'd': 4}