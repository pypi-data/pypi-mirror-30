import devconfig

def test_multiple_yamls_is_merged():
    devconfig.merges['tests.samples.merged2']._with('tests.samples.merged0')
    from tests.samples import merged2
    assert merged2.a == {'b': 5, 'c': 2}


def test_multiple_yamls_with_intermediate_module_name_is_merged():
    devconfig.merges['tests.samples.merged3']._with('tests.samples.merged1', 'tests.samples.merged0')
    from tests.samples import merged3
    assert merged3.a == {'b': 6, 'c': 2}
    assert merged3.d == 4


def test_multiple_yamls_with_intermediate_module_is_merged():
    from tests.samples import merged1
    devconfig.merges['tests.samples.merged3']._with(merged1, 'tests.samples.merged0')
    from tests.samples import merged3
    assert merged3.a == {'b': 6, 'c': 2}
    assert merged3.d == 4
