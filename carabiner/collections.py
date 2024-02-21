"""Useful data structures."""

from collections import UserDict
from itertools import chain

class MultiKeyDict(UserDict):

    """

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):

        args = chain.from_iterable(args)

        return {arg: self.data[arg] for arg in args}        