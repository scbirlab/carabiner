"""Tweaked casting between Python types."""

from typing import Any, List, TextIO, Union

from collections.abc import Iterable

from functools import singledispatch
from itertools import chain
import gzip
from io import StringIO, TextIOWrapper

from .itertools import batched


@singledispatch
def clist(x) -> List:

    """Cast an object to a list.

    Parameters
    ----------
    x : str or iterable
        Object to cast.

    Returns
    -------
    list

    Examples
    --------
    >>> clist('Hello world')
    ['Hello world']
    >>> clist(('Hello', 'world'))  # doctest: +SKIP
    ['Hello', 'world']
    
    """

    return list(x)


@clist.register
def _(x: str) -> List[str]:

    return [x]


@clist.register
def _(x: int) -> List[int]:

    return [x]


@clist.register
def _(x: float) -> List[float]:

    return [x]
    
    
@clist.register
def _(x: TextIOWrapper) -> List[TextIOWrapper]:

    return [x]
    

@singledispatch
def cio(x, *args, **kwargs) -> TextIOWrapper:

    r"""Cast an object to a file-like object.

    Addtional parameters are passed to `open` or `gzip.open`.

    If the input is a string, then it is treated as a filename. If it ends
    in `.gz` or `.gzip`, then it is assumed to be a GZIP-compressed file.

    If the input is an open file, then the file is closed and reopened with 
    the provided parameters. This can be useful to close for writing and 
    open for reading.

    If the input is a `io.StringIO` object, then the cursor is moved to the
    start and the object is returned.

    Parameters
    ----------
    x : str or iterable
        Object to cast.

    Returns
    -------
    TextIOWrapper

    Examples
    --------
    >>> cio('Hello.txt')  # doctest: +SKIP
    <_io.TextIOWrapper name='Hello.txt' mode='r' encoding='UTF-8'>
    >>> cio('Hello.txt', 'w')
    <_io.TextIOWrapper name='Hello.txt' mode='w' encoding='UTF-8'>
    >>> list(cio(StringIO("Hello\nworld")))
    ['Hello\n', 'world']

    """

    raise TypeError(f"Can't force object of type {type(x).__name__} "
                     "to be a file-like")


@cio.register
def _(x: str, *args, **kwargs):

    if x.endswith('.gz') or x.endswith('.gzip'):

        return gzip.open(x, *args, **kwargs)

    else:

        return open(x, *args, **kwargs)


@cio.register
def _(x: TextIOWrapper, *args, **kwargs):

    x.close()

    return cio(x.name, *args, **kwargs)


@cio.register
def _(x: StringIO, *args, **kwargs):

    x.seek(0)

    return x


@singledispatch
def cstr(x) -> str:

    """Cast an object to a string.

    If the object is a file-like object, return the filename.

    Parameters
    ----------
    x 
        Object to cast.

    Returns
    -------
    str

    Examples
    --------
    >>> cstr(["Hello", "world"])
    "['Hello', 'world']"
    >>> cstr(open("test/test-file.txt", "w"))
    'test/test-file.txt'
    
    """

    return str(x)


@cstr.register
def _(x: TextIOWrapper):

    return x.name   


CASTING_FUNCTIONS = dict(str=cstr, 
                         list=clist, 
                         TextIO=cio,
                         TextIOWrapper=cio)

def _cast_base(object: Any,
               to: str,
               *args, **kwargs):

    try:

        casting_function = CASTING_FUNCTIONS[to]

    except KeyError:

        raise TypeError(f"Cannot cast {type(object).__name__} to {to}.")

    return casting_function(object, 
                            *args, **kwargs)


@singledispatch
def _cast(to, 
          object: Any, 
          *args, **kwargs) -> Any:
    
    return _cast_base(object, str(to),
                      *args, **kwargs)


@_cast.register
def _(to: type, 
      object: Any, 
      *args, **kwargs) -> Any:
    
    return _cast_base(object, to.__name__,
                      *args, **kwargs)


@_cast.register
def _(to: str, 
      object: Any, 
      *args, **kwargs) -> Any:
    
    return _cast_base(object, to,
                      *args, **kwargs)
        

def cast(object: Any, 
         to: Union[str, type], 
         *args, **kwargs) -> Any:

    """Cast an object to another type.

    Parameters
    ----------
    x 
        Object to cast.
    to : str, type
        Type to cast to. Available: `str`, `list`, `TextIO`, `TextIOWrapper`

    Returns
    -------
        Casted object.

    Raises
    ------
    TypeError
        If the object cannot be casted to the type.

    Examples
    --------
    >>> cast("abc", list)
    ['abc']
    >>> cast(["abc"], 'str')
    "['abc']"

    """

    return _cast(to, object=object, 
                 *args, **kwargs)
    

@singledispatch
def flatten(x) -> Any:

    """Return the only item for iterables of length one.

    If `x` is a lazy iterator, then this returns a lazy iterator if more
    than one item in `x`.

    Parameters
    ----------
    x : str, iterable
        Object to flatten.

    Returns
    -------
    iterable or item
    
    Raises
    ------
    TypeError
        If `x` is not a supported type.

    Examples
    --------
    >>> flatten("Hello")
    'Hello'
    >>> flatten(["Hello"])
    'Hello'
    >>> flatten(["Hello", "world"])
    ['Hello', 'world']
    >>> flatten(tuple('abc'))
    ('a', 'b', 'c')
    >>> list(flatten(range(3)))
    [0, 1, 2]
    >>> flatten(range(1))
    0
    
    """

    raise TypeError(f"Cannot flatten object of type {type(x).__name__}.")


@flatten.register
def _(x: list) -> Any:

    if len(x) == 1:

        return x[0]
    
    else:

        return x
    

@flatten.register
def _(x: str) -> Any:

    return x


@flatten.register
def _(x: int) -> Any:

    return x


@flatten.register
def _(x: float) -> Any:

    return x


    
@flatten.register
def _(x: tuple) -> Any:

   return tuple(flatten(list(x)))
    

@flatten.register
def _(x: set) -> Any:

    if len(x) == 1:

        return list(x)[0]
    
    else:

        return x


@flatten.register
def _(x: Iterable) -> Any:

    iterators = []
    make_list = True

    for i, batch in enumerate(batched(x, 1000)):
        
        if make_list:
            batch = list(batch)

        if i == 0:
            
            if len(batch) == 1:

                return batch[0]

            else:

                make_list = False

        iterators.append(batch)

    return chain.from_iterable(iterators) 
