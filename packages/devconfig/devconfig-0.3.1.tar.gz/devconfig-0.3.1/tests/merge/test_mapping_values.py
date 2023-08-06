import devconfig.mapping

def test_value_mapping_replaced_with_value_simple():
    assert devconfig.mapping.merge({ 5:8 }, {5:{6:7}}) == { 5:8 }


def test_value_simple_replaced_with_value_mapping():
    assert devconfig.mapping.merge({5:{6:7}}, {5:8}) == {5:{6:7}}


def test_multiarg_value_mapping_replaced_with_value_simple():
    assert devconfig.mapping.merge({ 5:8 }, {5:{6:8}}, {5:{6:7}}) == { 5:8 }


def test_multiarg_value_mapping_replaced_with_intermediate_value_simple():
    assert devconfig.mapping.merge({5:{6:8}}, { 5:8 }, {5:{6:7}}) == {5:{6:8}}


def test_multiarg_value_simple_replaced_with_value_mapping():
    assert devconfig.mapping.merge({5:{6:7}}, {5:{6:8}}, {5:8}) == {5:{6:7}}


def test_subnested_value_mapping_replaced_with_value_simple():
    assert devconfig.mapping.merge({0:{5:8}}, {0:{5:{6:8}}}, {0:{5:{6:7}}}) == {0:{5:8}}


def test_subnested_value_simple_replaced_with_value_mapping():
    assert devconfig.mapping.merge({0:{5:{6:7}}}, {0:{5:{6:8}}}, {0:{5:8}}) == {0:{5:{6:7}}}


def test_subnested_value_simple_replaced_with_intermediate_value_mapping():
    assert devconfig.mapping.merge({0:{5:{6:7}}}, {0:{5:8}}, {0:{5:{6:8}}}) == {0:{5:{6:7}}}