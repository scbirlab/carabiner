"""Miscellaneous utilities."""

from typing import Any, Iterable, Mapping, Tuple, Union
import sys

from tqdm.auto import tqdm

_CBPAL = ('#EE7733', '#0077BB', '#33BBEE', 
          '#EE3377', '#CC3311', '#009988', 
          '#BBBBBB', "#000000")

def colorblind_palette(i: Union[int, slice, Iterable, None] = None) -> Tuple[str]:

    """Provide hexadecimal codes for a colourblind-friendly qualitative palette.

    Parameters
    ----------
    i : int, slice, range, optional
        Index(es) of colors to return. If not supplied, returns all.

    Returns
    -------
    tuple
        Sequence of colors encoded as hexadecimals.
    
    Examples
    --------
    >>> colorblind_palette(range(2))
    ('#EE7733', '#0077BB')
    >>> colorblind_palette(slice(2))
    ('#EE7733', '#0077BB')
    >>> colorblind_palette()
    ('#EE7733', '#0077BB', '#33BBEE', '#EE3377', '#CC3311', '#009988', '#BBBBBB', '#000000')
    
    """

    if i is None:

        return _CBPAL
    
    elif isinstance(i, slice) or isinstance(i, int):

        return _CBPAL[i]
    
    elif isinstance(i, Iterable):

        return tuple(_CBPAL[j] for j in i)


def tenumerate(x: Iterable[Any], 
               *args, **kwargs) -> Iterable[Any]:
    
    """Enumerate with a progress bar.
    
    """

    return enumerate(tqdm(x, *args, **kwargs))


def print_err(*args, **kwargs) -> None:

    """Print to stderr instead of stdout.
    
    """

    return print(*args, **kwargs, 
                 file=sys.stderr)


def pprint_dict(x: Mapping, 
                message: Union[str, None] = None) -> None:
    
    """Pretty-print a dictionary to stderr, optionally prepended with a message.

    Useful for summarizing command line arguments.

    Parameters
    ----------
    x : dictionary
        Key-value pairs to print.
    message : str, optional
        Message to prepend.

    Examples
    --------
    >>> d = {"option A": 1, "option B": True, "option C": "Nothing"}  # doctest: +NORMALIZE_WHITESPACE
    >>> pprint_dict(d)
            option A: 1
            option B: True
            option C: Nothing
    >>> pprint_dict(d, message="Your options")  # doctest: +NORMALIZE_WHITESPACE
    Your options:
            option A: 1
            option B: True
            option C: Nothing

    """
    
    key_val_str = (f'{key}: {val:.2f}' if isinstance(val, float) else f'{key}: {val}'
                   for key, val in x.items())
    
    if message is not None:
        message = f'{message}:\n\t'
    else:
        message = '\t'

    return print_err(message + '\n\t'.join(key_val_str))