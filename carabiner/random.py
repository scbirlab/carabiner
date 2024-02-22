"""Tools for randomness."""

from typing import Iterable, List

from math import log, log1p, floor
from random import random, randrange, shuffle
from itertools import islice


def sample_iter(iterable: Iterable, 
                k: int = 1, 
                shuffle_output:bool = True) -> List:

    """Random sampling from an iterable of unknown length without needing it to be held entirely in
    memory.

    This allows sampling from an iterable without needing the iterable to be held entirely in
    memory at one time and without knowing the length of the iterable ahead of
    time. A typical case might be selecting lines from a large text file while
    reading the file in a single pass.

    One limitation is that the sampled population must fit in memory.

    Based in Reservoir Sampling: https://en.wikipedia.org/wiki/Reservoir_sampling

    Originally written here: https://bugs.python.org/issue41311

    Based on GitHub Gist: https://gist.github.com/oscarbenjamin/4c1b977181f34414a425f68589e895d1
    
    Parameters
    ----------
    iterable : Iterable
        Sequence of items which may or may not be held in memory.
    k : int, optional
        Number of items to sample. Default: 1.
    shuffle_output : bool, optional
        Return items in random order (default). Otherwise return in
        original order.

    Returns
    -------
    list
        Sequence sampled from `iterable`.

    Examples
    --------
    >>> from string import ascii_letters
    >>> from itertools import chain
    >>> from random import seed
    >>> seed(1)
    >>> sample_iter(chain.from_iterable(ascii_letters for _ in range(1000000)), 10)
    ['X', 'c', 'w', 'q', 'T', 'e', 'u', 'w', 'E', 'h']
    >>> seed(1)
    >>> sample_iter(chain.from_iterable(ascii_letters for _ in range(1000000)), 10, shuffle_output=False)
    ['T', 'h', 'u', 'X', 'E', 'e', 'w', 'q', 'c', 'w']

    """

    iterator = iter(iterable)
    values = list(islice(iterator, k))

    irange = range(len(values))
    indices = dict(zip(irange, irange))

    kinv, W = 1. / k, 1.

    while True:

        W *= random() ** kinv

        # random() < 1.0 but random() ** kinv might not be
        # W == 1.0 implies "infinite" skips
        if W >= 1.:
            break

        # skip is geometrically distributed with parameter W
        skip = floor( log(random())/log1p(-W) )
        try:
            newval = next(islice(iterator, skip, skip+1))
        except StopIteration:
            break

        # Append new, replace old with dummy, and keep track of order
        remove_index = randrange(k)
        values[indices[remove_index]] = None
        indices[remove_index] = len(values)
        values.append(newval)

    values = [values[indices[i]] for i in irange]

    if shuffle_output:
        shuffle(values)

    return values