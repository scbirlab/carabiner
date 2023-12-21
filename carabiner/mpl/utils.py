"""Utilities for matplotlib."""

from typing import Tuple

import matplotlib.pyplot as plt
from matplotlib import figure, axes


def grid(nrow: int = 1, 
         ncol: int = 1, 
         panel_size: float = 3., 
         aspect_ratio: float = 1., 
         layout: str = 'constrained',
         *args, **kwargs) -> Tuple[figure.Figure, axes.Axes]:
    
    """Create a figure and a set of subplots with sensible defaults.

    
    """

    return plt.subplots(nrow, ncol, 
                        figsize=(ncol * panel_size * aspect_ratio,
                                 nrow * panel_size),
                        layout=layout,
                        *args, **kwargs)