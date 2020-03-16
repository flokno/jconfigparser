import operator
from functools import reduce

from jconfigparser.dict import DotDict


def test_setitem():
    d = DotDict()
    key = "a"
    value = 0

    d[key] = value

    for ii, k in enumerate(["b", "c", "d"]):
        key = f"{key}.{k}"
        value = ii + 1
        d[key] = value

        assert d[key] == value


def test_getitem():
    keys = "a.b.c.d"
    value = "sth"
    d = DotDict()
    d[keys] = "sth"

    for ii, _ in enumerate(keys.split(".")):
        view = reduce(operator.getitem, keys.split(".")[:ii], d)
        assert isinstance(view, DotDict)

    assert d[keys] == value
