"""Miscellaneous utilities."""

from typing import Any, Iterable, Mapping, Tuple, Optional

from itertools import chain

import sys

__all__ = ["colorblind_palette", "print_err", "pprint_dict", "upper_and_lower"]

TOL_PALETTES = {
    "vibrant": (
        "#0077BB", 
        "#33BBEE", 
        "#009988", 
        "#EE7733", 
        "#CC3311", 
        "#EE3377", 
        "#BBBBBB", 
        "#000000",
    ),
    "vibrant_0": (
        "#EE7733", 
        "#0077BB", 
        "#33BBEE", 
        "#EE3377", 
        "#CC3311", 
        "#009988", 
        "#BBBBBB", 
        "#000000",
    ),
    "muted": (
        "#332288",
        "#88CCEE",
        "#44AA99",
        "#117733",
        "#999933",
        "#DDCC77",
        "#CC6677",
        "#882255",
        "#AA4499",
        "#DDDDDD",
    ),
    "bright": (
        "#4477AA",
        "#66CCEE",
        "#228833",
        "#CCBB44",
        "#EE6677",
        "#AA3377",
        "#BBBBBB",
    ),
    "medium contrast": (
        "#FFFFFF",
        "#EECC66",
        "#EE99AA",
        "#6699CC",
        "#997700",
        "#994455",
        "#004488",
        "#000000",
    )
}

DEFAULT_PALETTE = "vibrant"

def colorblind_palette(
    i: Optional[Any] = None,
    name: str = DEFAULT_PALETTE
) -> Tuple[str]:

    """Provide hexadecimal codes for Tol's colorblind-friendly qualitative palette.

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
    >>> colorblind_palette(range(2), name="vibrant_0")
    ('#EE7733', '#0077BB')
    >>> colorblind_palette(range(2))
    ('#0077BB', '#33BBEE')
    >>> colorblind_palette(slice(3, 6))
    ('#EE7733', '#CC3311', '#EE3377')
    >>> colorblind_palette(name="vibrant_0")
    ('#EE7733', '#0077BB', '#33BBEE', '#EE3377', '#CC3311', '#009988', '#BBBBBB', '#000000')
    >>> colorblind_palette(name="muted")
    ('#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499', '#DDDDDD')
    
    """

    return _colorblind_palette(i=i, name=name)


def _colorblind_palette(
    i: Any,
    name: str = DEFAULT_PALETTE
) -> Tuple[str]:
    pal = TOL_PALETTES.get(name, TOL_PALETTES[DEFAULT_PALETTE])
    if i is None:
        return pal
    if isinstance(i, Iterable):
        return tuple(pal[j] for j in i)
    elif isinstance(i, (slice, int)):
        return pal[i]
    else:
        raise NotImplementedError(f"No method for colorblind_palette for type {type(i)}: {i}.")


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