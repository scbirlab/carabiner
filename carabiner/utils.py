"""Miscellaneous utilities."""

from typing import Any, Iterable, Mapping, Tuple, Optional

from functools import singledispatch
from itertools import chain

import sys

__all__ = ["colorblind_palette", "print_err", "pprint_dict", "upper_and_lower"]

_CBPAL = ('#EE7733', '#0077BB', '#33BBEE', 
          '#EE3377', '#CC3311', '#009988', 
          '#BBBBBB', "#000000")

def colorblind_palette(i: Optional[Any] = None) -> Tuple[str]:

    """Provide hexadecimal codes for a colorblind-friendly qualitative palette.

    Parameters
    ----------
    i : int, slice, iterable, optional
        Index(es) of colors to return. If not supplied, returns all.

    Returns
    -------
    tuple
        Sequence of colors encoded as hexadecimals.

    Raises
    ------
    NotImplementedError
        If `i` is not an integer, slice, or iterable.
    
    Examples
    --------
    >>> colorblind_palette(range(2))
    ('#EE7733', '#0077BB')
    >>> colorblind_palette(slice(3, 6))
    ('#EE3377', '#CC3311', '#009988')
    >>> colorblind_palette()
    ('#EE7733', '#0077BB', '#33BBEE', '#EE3377', '#CC3311', '#009988', '#BBBBBB', '#000000')
    
    """

    return _colorblind_palette(i)
    

@singledispatch
def _colorblind_palette(i: Any):
    
    try:
        return tuple(_CBPAL[j] for j in i)
    except:
        raise NotImplementedError(f"No method for colorblind_palette for type {type(i)}: {i}.")
    

@_colorblind_palette.register
def _(i: None) -> Tuple[str]:

    return _CBPAL


@_colorblind_palette.register
def _(i: slice) -> Tuple[str]:

    return _CBPAL[i]


@_colorblind_palette.register
def _(i: int) -> Tuple[str]:

    return _CBPAL[i]


def print_err(*args, **kwargs) -> None:

    r"""Print to stderr instead of stdout.

    Arguments are passed to standard `print`.

    Returns
    -------
    None

    Examples
    --------
    >>> print_err("Hello world!")  # doctest: +SKIP
    Hello world!
    >>> print_err("Hello world!", end='~\n')  # doctest: +SKIP
    Hello world!~
    >>> print_err("Hello", "world!", end='~\n')  # doctest: +SKIP
    Hello world!~

    """

    return print(*args, **kwargs, 
                 file=sys.stderr)


def pprint_dict(object: Mapping, 
                message: Optional[str] = None) -> None:
    
    """Pretty-print a dictionary to stderr, optionally prepended with a message.

    Can accept either a dictionary or an object with a `__dict__` attribute. Useful for 
    summarizing command line arguments.

    Parameters
    ----------
    object : dict or object
        Dictionary or object to print.
    message : str, optional
        Message to prepend.

    Raises
    ------
    TypeError
        If `object` is not a dictionary or not an object with a `__dict__` attribute.

    Examples
    --------
    >>> d = {"option A": 1, "option B": True, "option C": "Nothing"}  
    >>> pprint_dict(d)  # doctest: +SKIP
            option A: 1
            option B: True
            option C: Nothing
    >>> pprint_dict(d, message="Your options")  # doctest: +SKIP
    Your options:
            option A: 1
            option B: True
            option C: Nothing

    """

    if not isinstance(object, dict):
        try:
            object = vars(object)
        except TypeError:
            raise TypeError("Input to pprint_dict is not a dict and "
                            "does not have a __dict__ attribute.\n\t"
                            "Attributes: {}".format(', '.join(dir(object))))
    
    key_val_str = (f'{key}: {val}' for key, val in object.items())
    
    if message is not None:
        message = f'{message}:\n\t'
    else:
        message = '\t'

    return print_err(message + '\n\t'.join(key_val_str))


def upper_and_lower(x: Iterable[str], 
                    sort: bool = True) -> Tuple[str]:

    """Convert a list of strings into the unique set of uppercase and 
    lowercase versions.

    Useful for listing command-line options which are case-insensitive.

    Parameters
    ----------
    x : Iterable of strings
        Strings to convert.
    sort : bool, optional
        Whether to sort the output. Default: `True`

    Returns
    -------
    tuple
        Set of unique lowercase and uppercase strings.

    Examples
    --------
    >>> upper_and_lower(["A", "B"])
    ('A', 'B', 'a', 'b')
    >>> upper_and_lower(["Cat", "dog"])
    ('CAT', 'Cat', 'DOG', 'cat', 'dog')
    
    """

    upper, lower = (tuple(map(f, x)) for f in (str.upper, str.casefold))
    unique_strings = set(chain(x, upper, lower))

    if sort:
        return tuple(sorted(unique_strings))
    else:
        return tuple(unique_strings)