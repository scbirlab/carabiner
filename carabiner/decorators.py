"""Decorators to faciltiate functional programming."""

from typing import Any, Callable, Iterable, Optional

from functools import wraps

from .cast import cast, flatten

TDecorator = Callable[[Callable, Any], Callable]

def decorator_with_params(decorator: TDecorator) -> TDecorator:

    """Convert a decorator to be used with optional parameters.

    Can itself be used as a decorator.

    The input decorator should take a function as its first argment, and
    further optional parameters. This `decorator_with_params` will 
    return a decorator that can be used with or without specifying the optional
    parameters. (Normally this a very convoluted code.)

    Parameters
    ----------
    decorator : Callable
        Decorator to convert.

    Returns
    -------
    Callable
        Converted decorator.

    Examples
    --------
    >>> def decor(f, suffix="World"): return lambda x: f(x + suffix)
    ...
    >>> @decor
    ... def printer(x): print(x)
    ... 
    >>> @decor(suffix="everyone") 
    ... def printer2(x): print(x)
    ... 
    Traceback (most recent call last):
        ...
    TypeError: decor() missing 1 required positional argument: 'f'
    >>> decor2 = decorator_with_params(decor)
    >>> @decor2(suffix="everyone")
    ... def printer3(x): print(x)
    ... 
    >>> printer("Hello ")
    Hello World
    >>> printer3("Hello ")
    Hello everyone

    """

    @wraps(decorator)
    def _parameterized_decorator(decorated_function: Optional[Callable] = None,
                                 *args, **kwargs) -> Callable:

        @wraps(decorated_function)
        def _decorated_function(f):

            return decorator(f, *args, **kwargs)

        return (decorator(decorated_function,  *args, **kwargs) 
                if callable(decorated_function) 
                else _decorated_function)

    return _parameterized_decorator


@decorator_with_params
def return_none_on_error(f: Callable, 
                         exception: Optional[Exception] = None) -> Callable:
    
    """Force a function to return None instead of raising an exception.

    Parameters
    ----------
    f : Callable, optional
        Function to convert. If not provided, returns a decorator.
    exception : Exception, optional
        Exception type to bypass. Default: all exceptions.

    Returns
    -------
    Callable
        If f is provided, then decorated f. Otherwise returns a decorator.

    Examples
    --------
    >>> def error_maker(x): raise KeyError
    ... 
    >>> @return_none_on_error
    ... def error_maker2(x): raise KeyError
    ... 
    >>> @return_none_on_error(exception=ValueError)
    ... def error_maker3(x): raise KeyError
    ... 
    >>> error_maker('a')  
    Traceback (most recent call last):
        ...
    KeyError
    >>> error_maker2('a')
    >>> error_maker3('a') 
    Traceback (most recent call last):
        ...
    KeyError

    """
    
    exception = exception or Exception
    
    @wraps(f)
    def wrapped_function(*args, **kwargs):

        try:
            return f(*args, **kwargs)
        except exception:
            return None

    return wrapped_function


def vectorize(f: Callable) -> Callable:

    """Convert a scalar function into a vectorized mapping function.

    The converted function returns a lazy iterable if passed an iterable, 
    and a scalar if passed a scalar.

    Parameters
    ----------
    f : Callable
        Scalar function to convert.

    Returns
    -------
    Callable
        Vectorized function.

    Examples
    --------
    >>> @vectorize
    ... def vector_adder(x): return x + 1
    ...
    >>> list(vector_adder(range(3)))
    [1, 2, 3]
    >>> list(vector_adder((4, 5, 6)))
    [5, 6, 7]
    >>> vector_adder([10])
    11
    >>> vector_adder(10)
    11

    """

    @wraps(f)
    def vectorized_function(arg0: Any, 
                            *args, **kwargs) -> Iterable:

       arg0 = cast(arg0, to=list)

       return flatten(f(_x, *args, **kwargs) for _x in arg0)
        
    return vectorized_function

