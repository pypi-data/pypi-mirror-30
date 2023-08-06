import devconfig

def test_yaml_module_hook():
    devconfig.hooks['tests.samples.merged4']._with(lambda module: module.hookdict.update({'b': 2}))
    from tests.samples import merged4
    assert merged4.hookdict == {'a': 1, 'b': 2}


def test_yaml_module_intermediate_hook():
    devconfig.merges['tests.samples.merged6']._with('tests.samples.merged5')
    devconfig.hooks['tests.samples.merged6']._with(lambda module: module.hookdict.update({'b': 2}))
    from tests.samples import merged6
    devconfig.merges['tests.samples.merged7']._with(merged6)

    from tests.samples import merged7
    assert merged7.hookdict == {'a':1, 'b': 2, 'c': 3, 'd': 4}