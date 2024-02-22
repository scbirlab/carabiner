"""Useful data structures."""

from collections import UserDict
from itertools import chain

class MultiKeyDict(UserDict):

    """Dictionary where multiple keys can be accessed at once.

    Examples
    --------
    >>> d = MultiKeyDict(a=1, b=2, c=3)
    >>> d
    {'a': 1, 'b': 2, 'c': 3}
    >>> d['c']
    {'c': 3}
    >>> d['a', 'b']
    {'a': 1, 'b': 2}

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


    def __getitem__(self, *args, **kwargs):

        args = chain.from_iterable(args)

        return {arg: self.data[arg] for arg in args}        