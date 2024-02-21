"""Decorators to faciltiate functional programming."""

from typing import Any, Callable, Iterable, Optional

from functools import wraps

from .cast import cast, flatten

TDecorator = Callable[[Callable, Any], Callable]

def decorator_with_params(decorator: TDecorator) -> TDecorator:

    """

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

    """Turn a scalar function into a vectorized mapping function.
    
    """

    @wraps(f)
    def vectorized_function(arg0: Any, 
                            *args, **kwargs) -> Iterable:

       arg0 = cast(arg0, to=list)

       return flatten(f(_x, *args, **kwargs) for _x in arg0)
        
    return vectorized_function

