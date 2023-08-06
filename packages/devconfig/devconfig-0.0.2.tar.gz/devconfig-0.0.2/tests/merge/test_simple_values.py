import devconfig.mapping


def test_extended_with_other_values_on_merge():
    assert devconfig.mapping.merge({1:2}, {3:4}) == {1:2, 3:4}


def test_merge_value_replaced_with_simple_value_of_same_type():
    assert devconfig.mapping.merge({5:{6:8}}, {5:{6:7}}) == {5:{6:8}}


def test_merge_value_replaced_with_simple_value_of_other_simple_type():
    assert devconfig.mapping.merge({5:{6:None}}, {5:{6:7}}) == {5:{6:None}}


def test_multiarg_extended_with_other_values_on_merge():
    assert devconfig.mapping.merge({5:6}, {3:4}, {1:2}) == {1:2,3:4,5:6}


def test_multiarg_merge_value_replaced_with_simple_value_of_same_type():
    assert devconfig.mapping.merge({5:{6:9}}, {5:{6:8}}, {5:{6:7}}) == {5:{6:9}}


def test_multiarg_merge_value_replaced_with_simple_value_of_other_simple_type():
    assert devconfig.mapping.merge({5:{6:False}}, {5:{6:None}}, {5:{6:7}}) == {5:{6:False}}


def test_subnested_extended_with_other_values_on_merge():
    assert devconfig.mapping.merge({0:{3:4}}, {0:{1:2}}) == {0:{1:2,3:4}}


def test_subnested_merge_value_replaced_with_simple_value_of_same_type():
    assert devconfig.mapping.merge({0:{5:{6:8}}}, {0:{5:{6:7}}}) == {0:{5:{6:8}}}


def test_subnested_merge_value_replaced_with_simple_value_of_other_simple_type():
    assert devconfig.mapping.merge({0:{5:{6:None}}}, {0:{5:{6:7}}}) == {0:{5:{6:None}}}
