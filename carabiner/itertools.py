"""Utilities for iterables."""

from typing import Any, Iterable

from itertools import islice

from tqdm.auto import tqdm

def batched(iterable: Iterable[Any], 
            n: int) -> Iterable[Iterable[Any]]:

    """Copy of the Python function for versions where it's not available.

    # batched('ABCDEFG', 3) --> ABC DEF G

    Parameters
    ----------
    iterable : Iterable
        Iterable to batch.
    n : int
        Batch size.

    Returns
    -------
    Iterable
        Iterable of iterables with size `n`.

    Examples
    --------
    >>> for batch in batched('abcdef', 3): print(list(batch))
    ... 
    ['a', 'b', 'c']
    ['d', 'e', 'f']
    
    """
   
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def tenumerate(x: Iterable[Any], 
               *args, **kwargs) -> Iterable[Any]:
    
    """Standard `enumerate` but with a progress bar.

    Additional arguments are passed to `tqdm.tqdm`.

    Parameters
    ----------
    iterable : Iterable
        Iterable to enumerate.

    Returns
    -------
    Iterable
        Iterable of tuples containing index and item.
    
    """

    return enumerate(tqdm(x, *args, **kwargs))