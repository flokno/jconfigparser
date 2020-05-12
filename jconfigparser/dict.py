import operator
from functools import reduce

BASE_DICT = dict

key_separator = "."
private_prefix = "_"
attribute_access = True
strict = False
empty = None


class DotDict(BASE_DICT):
    """dict with dot access and assignment

    some tricks from https://stackoverflow.com/a/14692747/5172579
    """

    key_separator = key_separator
    private_prefix = private_prefix
    strict = strict
    empty = empty

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if attribute_access:
            self.__dict__ = self

    def __getitem__(self, key):
        keys = self._keys(key)
        return reduce(dict.__getitem__, keys, self)

    def __setitem__(self, key, value):
        # populate tree
        *keys, last_key = self._keys(key)

        self._build_tree(key)
        d = reduce(operator.getitem, keys, self)

        if isinstance(d.get(last_key), dict) and self.strict:
            raise ValueError(f"{key} is a dict, danger of losing depth.")

        new_dict = DotDict({last_key: value})

        keys = [*keys, last_key]

        d = reduce(operator.getitem, keys[:-1], self)

        if isinstance(d, DotDict):
            d.update(new_dict)
        else:
            d = new_dict

    def _build_tree(self, key):
        # i) build tree of dicts
        try:
            first_key, *keys, last_key = self._keys(key)
        except ValueError:
            return

        def make_dict(d):
            if not isinstance(d, DotDict):
                d = DotDict()

        # make sure each level exists
        # i) create top level if it does not exist
        if first_key in self and isinstance(self.get(first_key), DotDict):
            pass
        else:
            dict.__setitem__(self, first_key, DotDict())

        # check level by level and create empty dicts where needed
        # `d` is the current view on `self`
        for ii, key in enumerate(keys):
            d = reduce(operator.getitem, [first_key, *keys[:ii]], self)

            # d has to be a dict:
            if not isinstance(d, DotDict):
                d = DotDict()

            # add level
            if key not in d:
                dict.__setitem__(d, key, DotDict())

        # set the last level w/o destroying deeper levels
        # https://stackoverflow.com/a/43499625/5172579
        keys = [first_key, *keys]
        next_last_key = keys[-1]
        d = reduce(operator.getitem, keys[:-1], self)

        # d has to be a dict:
        if not isinstance(d[next_last_key], DotDict):
            d[next_last_key] = DotDict()

        if not d[next_last_key]:
            d[next_last_key].update(DotDict({last_key: self.empty}))

    def _keys(self, key):
        return key.split(self.key_separator)

    def to_dict(self):
        """ (recursively) return plain python dictionary """
        rep = {}
        for key, val in self.items():
            if private_prefix is not None and key.startswith(self.private_prefix):
                continue
            if isinstance(val, DotDict):
                val = val.to_dict()
            rep.update({key: val})

        return rep
