"""Tweaked casting between Python types."""

from typing import Any, List, TextIO, Union

from collections.abc import Iterable

from functools import singledispatch
from itertools import chain
import gzip
from io import TextIOWrapper

from .itertools import batched


@singledispatch
def clist(x) -> List:

    """
    
    """

    return [x]


@clist.register
def _(x: str) -> List:

    return [x]
    
    
@clist.register
def _(x: list) -> List:

    return x


@clist.register
def _(x: tuple) -> List:

    return list(x)


@clist.register
def _(x: set) -> List:

    return list(x)


@clist.register
def _(x: Iterable) -> List:

    return list(x)
    

@singledispatch
def cio(x, *args, **kwargs) -> TextIOWrapper:

    """
    
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
def _(x: TextIO, *args, **kwargs):

    x.close()

    return cio(x.name, *args, **kwargs)


@singledispatch
def cstr(x, *args, **kwargs) -> str:

    return str(x)


@cstr.register
def _(x: TextIO, *args, **kwargs):

    return x.name


@singledispatch
def flatten(x) -> Any:

    raise TypeError(f"Cannot flatten object of type {type(x).__name__}.")


@flatten.register
def _(x: list) -> Any:

    if len(x) == 1:

        return x[0]
    
    else:

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


CASTING_FUNCTIONS = dict(str=cstr, 
                         list=clist, 
                         TextIO=cio)

def _cast(obj: Any, 
          to: str, *args, **kwargs) -> Any:

    try:

        casting_function = CASTING_FUNCTIONS[to]

    except KeyError:

        raise TypeError(f"Cannot cast {type(obj).__name__} to {to}.")

    return casting_function(obj, *args, **kwargs)
        

def cast(obj: Any, 
         to: Union[str, type], *args, **kwargs) -> Any:

    """
        
    """

    if isinstance(to, type):

        return _cast(obj, to.__name__, *args, **kwargs)

    elif isinstance(to, str):

        return _cast(obj, to, *args, **kwargs)

    else:

        return _cast(obj, str(to), *args, **kwargs)
