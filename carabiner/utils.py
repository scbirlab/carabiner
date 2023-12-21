"""Miscellaneous utilities."""

from typing import Any, Iterable, Mapping
import sys

from tqdm.auto import tqdm


def tenumerate(x: Iterable[Any]) -> Iterable[Any]:

    return tqdm(enumerate(x))


def print_err(*args, **kwargs) -> None:

    return print(*args, **kwargs, 
                 file=sys.stderr)


def pprint_dict(x: Mapping, 
                message: str) -> None:
    
    key_val_str = (f'{key}: {val:.2f}' if isinstance(val, float) else f'{key}: {val}'
                   for key, val in x.items())

    return print_err(f'{message}:\n\t' + '\n\t'.join(key_val_str))