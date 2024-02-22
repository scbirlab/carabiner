"""Utilities for matplotlib."""

from typing import Tuple

try:
    import matplotlib.pyplot as plt
except ImportError:
    raise ImportError("\Matplotlib not installed. Try installing with pip:"
                      "\n$ pip install matplotlib\n"
                      "\nor reinstall carabiner with matplotlib:\n"
                      "\n$ pip install carabiner[mpl]\n")
else:
    from matplotlib import figure, axes

TFigAx = Tuple[figure.Figure, axes.Axes]

def grid(nrow: int = 1, 
         ncol: int = 1, 
         panel_size: float = 3., 
         aspect_ratio: float = 1., 
         layout: str = 'constrained',
         *args, **kwargs) -> TFigAx:
    
     """Create a figure and a set of subplots with sensible defaults.

     Additional arguments are passed to `matplotlib.pyplot.subplots()`.

     Parameters
     ----------
     nrow : int, optional
          Number of rows. Default: 1.
     ncol : int, optional
          Number of columns. Default: 1.
     panel_size : float, optional
          Size of panels. Default: 3.
     aspect_ratio : float
          Ratio of width over height. Default: 1. (square).
     layout : str
          Matplotlib `fig` layout. Default: "constrained".

     Returns
     -------
     tuple
          Pair of `figure.Figure` and `axes.Axes` objects.
    
     """

     return plt.subplots(nrow, ncol, 
                         figsize=(ncol * panel_size * aspect_ratio,
                                  nrow * panel_size),
                         layout=layout,
                         *args, **kwargs)