"""Utilities for iterables."""

from typing import Any, Iterable

from itertools import islice

from tqdm.auto import tqdm

def batched(iterable: Iterable[Any], 
            n: int) -> Iterable[Iterable[Any]]:

    """Copy of the Python function for versions where it's not available.

    # batched('ABCDEFG', 3) --> ABC DEF G
    
    """
   
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def tenumerate(x: Iterable[Any], 
               *args, **kwargs) -> Iterable[Any]:
    
    """Enumerate with a progress bar.
    
    """

    return enumerate(tqdm(x, *args, **kwargs))