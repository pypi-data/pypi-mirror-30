from mldata.lib.normalizer import Normalizer


def test_normalizer():
    norm = Normalizer([1, 2, 3, '?'], ['?'])
    print(norm.normalize_numerical_value())
