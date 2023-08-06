""" Main module of the package. """

from collections import defaultdict
from pandas import DataFrame
from typing import Dict, List, NewType, Tuple, Any


TypeDataFrame = NewType('TypeDataFrame', DataFrame)


def as_dataframe(dicts: Dict or List[Dict], separator: str='.') -> TypeDataFrame:
    """ Returns dataframe built from dictionaries

    The dictionaries may have as values simple objects (e.g. integers, strings), lists, or even other dictionaries.

    :param dicts: Dictionary or list of dictionaries.
    :param separator: Separator character to use when composite keys are converted to string. Composite keys arise
    when a nested dictionary is flattened. For example, a dictionary `{'a': 1, 'b': {'a': 2}}` with separator set to
    `.` will result in a dataframe with columns `a`, and `a.b`.
    :returns: Dataframe.
    """

    if isinstance(dicts, dict):
        dicts = [dicts]

    dataframe = DataFrame()

    for d in dicts:
        dataframeable_dict = _DataFrameableDict([d])

        keys = list(dataframeable_dict.keys())
        for k in keys:
            string_key = separator.join([str(el) for el in k])
            dataframeable_dict[string_key] = dataframeable_dict.pop(k)

        df = DataFrame(dataframeable_dict)
        dataframe = dataframe.append(df, ignore_index=False, verify_integrity=False)

    dataframe = dataframe.reset_index(drop=True)
    return dataframe


class _DataFrameableDict(defaultdict):
    """ A dictionary in the format accepted by `pandas.DataFrame` """

    def __init__(self, dicts: List[Dict]) -> None:
        """ Initialize a `_DataFrameableDict` object from supplied dictionaries

        :param dicts: A sequence of dictionaries.
        """

        if not all([isinstance(d, dict) for d in dicts]):
            raise TypeError('Cannot convert object of type %s to custom dict' % type(dicts))

        super().__init__(list)

        dicts = [_DataFrameableDict.flattened(d) for d in dicts]
        final_keys = set([k for d in dicts for k in d])

        for d in dicts:
            for k in final_keys:
                if isinstance(d[k], list):
                    self[k] += d[k]
                else:
                    self[k].append(d[k])

            self.impute_locf()

        self.drop_redundant_keys()

    def drop_redundant_keys(self) -> None:
        """ Drop redundant keys

        Redundant keys may arise from flattening nested dictionaries. For example, when creating a dataframeable
        dictionary from `[{'a': 1, 'b': {'a': 2}}]`, before dropping the redundant keys, the result will be
        `{('a',): [1], ('b',): [None], ('b', 'a'): [2]}`. Here, the key `('b',)` is redundant because its value is a
        list of `None`'s and because the original `b` contained a dictionary as value.

        :returns: Nothing, just side effects.
        """

        redundant_keys = set()
        keys = list(self.keys())

        for k in keys:
            for kk in keys:
                if len(k) >= len(kk):
                    continue

                if k == kk[0:len(k)] and all(not el for el in self[k]):
                    redundant_keys.add(k)
                    break

        for k in redundant_keys:
            del self[k]

    def impute_locf(self) -> None:
        """ Impute missing values using the Last Observation Carried Forward method

        For example, calling this method when `self` is `{('a',): [1, 2, 3], ('b',): [1, 2, 3, 4, 5]}` will modify
        `self` into `{('a',): [1, 2, 3, 3, 3], ('b',): [1, 2, 3, 4, 5]}`. Here, the last element of `('a',)` is
        carried forward into fourth and fifth position of the new `('a',)`.

        :returns: Nothing, just side effects.
        """
        max_length = max([len(self[k]) for k in self])

        for k in self:
            length = len(self[k])
            self[k].extend([self[k][length - 1]]*(max_length - length))

    @staticmethod
    def flattened(d: Dict) -> Dict[Tuple, Any]:
        """ Returns flattened dictionary

        Returns a flattened dictionary. A flattened dictionary has only non-dictionaries as values. The returned values
        may contain lists with different lengths, in which case an exception is raised.

        :param d: Dictionary that may be nested (e.g. a value is another dictionary, ad infinitum).
        :returns: Flattened dictionary, with keys being tuples and values being non-dictionaries.
        :raises: ValueError
        """
        flattened = defaultdict(lambda: None)

        for k, v in d.items():

            k = (k,)

            if isinstance(v, dict):
                for kk, vv in _DataFrameableDict.flattened(v).items():
                    flattened[k + kk] = vv
            elif isinstance(v, list) and all([isinstance(el, dict) for el in v]):
                for kk, vv in _DataFrameableDict(v).items():
                    flattened[k + kk] = vv
            else:
                flattened[k] = v

        if len(set([len(d[k]) for k in d if isinstance(d[k], list)])) > 1:
            raise ValueError('Values contain lists of different lengths. Unable to flatten such dictionary.')

        return flattened
