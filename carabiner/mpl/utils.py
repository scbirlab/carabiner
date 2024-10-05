"""Utilities for matplotlib."""

from typing import Any, Callable, Iterable, Mapping, Tuple, Optional, Union
from functools import wraps
import os

try:
    import matplotlib.pyplot as plt
except ImportError:
    raise ImportError("Matplotlib not installed. Try installing with pip:"
                      "\n\t$ pip install matplotlib\n"
                      "\nor reinstall carabiner with matplotlib:\n"
                      "\n\t$ pip install carabiner[mpl]\n")
else:
    from matplotlib import axes, cycler, figure, rcParams
    import numpy as np
    from pandas import DataFrame
from tqdm.auto import tqdm

from ..cast import cast
from ..utils import colorblind_palette as utils_colorblind_palette, print_err

TFigAx = Tuple[figure.Figure, axes.Axes]

colorblind_palette = utils_colorblind_palette

# Set default color cycle on import
rcParams['axes.prop_cycle'] = cycler(color=colorblind_palette())

def grid(
     nrow: int = 1, 
     ncol: int = 1, 
     panel_size: float = 3., 
     aspect_ratio: float = 1., 
     layout: str = 'constrained',
     sharex: Union[str, bool] = False,
     sharey: Union[str, bool] = False,
     hide_shared_ticks: bool = False,
     *args, **kwargs
) -> TFigAx:
    
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
          Ratio of width over height. Default: 1 (square).
     layout : str
          Matplotlib `fig` layout. Default: "constrained".
     hide_shared_ticks : bool, optional
          Whether to hide the ticks when axes have shared scales
          from setting `sharex` or `sharey`. Default: `False`.

     Returns
     -------
     tuple
          Pair of `figure.Figure` and `axes.Axes` objects.
    
     """
     figsize=(
          ncol * panel_size * aspect_ratio,
          nrow * panel_size,
     )
     fig, axes = plt.subplots(
          nrow, 
          ncol, 
          figsize=figsize,
          layout=layout,
          sharex=sharex,
          sharey=sharey,
          *args, **kwargs
     )
     if sharex: 
          for ax in axes:
               ax.xaxis.set_tick_params(labelbottom=True)
     if sharey:
          for ax in axes:
               ax.yaxis.set_tick_params(labelleft=True)
     return fig, axes

def scattergrid(
     df: DataFrame, 
     grid_columns: Union[str, Iterable[str]], 
     grid_rows: Optional[Union[str, Iterable[str]]] = None, 
     grouping: Optional[Union[str, Iterable[str]]] = None,
     log: Optional[Union[str, Iterable[str]]] = None,
     n_bins: int = 40,
     scatter_opts: Optional[Mapping[str, Any]] = None,
     legend_opts: Optional[Mapping[str, Any]] = None,
     *args, **kwargs
) -> TFigAx:

     """Create a scatter plot to compare sets of variables in a Pandas DataFrame.

     Similar to `pandas.plotting.scatter_matrix`, but with larger panels and control
     over which variables are log-scaled. 
     
     Additional arguments are passed to `grid()`.

     Parameters
     ----------
     df : pandas.DataFrame
          Data to plot.
     grid_columns : str | Iterable[str]
          Data columns to plot along the rows of the scatter grid. 
          Becomes the x-axes.
     grid_rows : str | Iterable[str], optional
          Data columns to plot down the columns of the scatter grid. 
          Becomes the y-axes. If not provided, uses `grid_columns` for
          all pair-wise comparison.
     grouping : str | Iterable[str], optional
          If provided, use these columns of `df` to make groups and plot each 
          data group as a differnt color.
     log : str | Iterable[str], optional
          If provided, plot these columns of `df` on a log scale.
     n_bins : int, optional
          Number of bin for histograms plotted on identity diagonal of the 
          scatter grid. Default: 40.
     scatter_opts : dict, optional
          Extra keyword arguments to pass to the Matplotlib scatter plots.
     legend_opts : dict, optional
          Extra keyword arguments to pass to the Matplotlib legend.

     Returns
     -------
     tuple
          Pair of `figure.Figure` and `axes.Axes` objects.

     Raises
     ------
     KeyError
          If no named columns are in `df`.
    
     """

     grid_columns = [name for name in cast(grid_columns, to=list) if name in df]
     grid_rows = grid_rows or grid_columns
     grid_rows = [name for name in cast(grid_rows, to=list) if name in df]
     all_names = sorted(set(grid_columns + grid_rows))

     log = log or []
     log = [name for name in cast(log, to=list) if name in all_names]

     _scatter_opts = {"s": 3.}
     _scatter_opts.update(scatter_opts or {})
     _legend_opts = {"loc": "center left", "bbox_to_anchor": (1., .5)}
     _legend_opts.update(legend_opts or {})

     if grouping is None:
          grouping = "__group__"
          df = df.assign(__group__=grouping).groupby(grouping)
          dummy_group = True
     else:
          grouping = sorted(set([
               g for g in cast(grouping, to=list) if g in df
          ]))
          if len(grouping) == 0:
               raise KeyError(f"No columns in grouping ({', '.join(grouping)}) were in the DataFrame ({', '.join(df)})!")
          df = df.groupby(grouping)
          dummy_group = False

     fig, axes = grid(
          nrow=len(grid_rows), 
          ncol=len(grid_columns),
          *args, **kwargs
     )
     for axrow, grid_row_name in zip(tqdm(axes), grid_rows):
          yscale = "log" if grid_row_name in log else "linear"
          for ax, grid_col_name in zip(axrow, grid_columns):
               xscale = "log" if grid_col_name in log else "linear"
               for group_name, group_df in df:
                    extras = {"label": group_name} if not dummy_group else {}
                    if grid_row_name == grid_col_name:
                         if xscale == "log":
                              values = group_df[grid_col_name].values
                              bins = np.geomspace(
                                   values.min(), 
                                   values.max(), 
                                   num=n_bins,
                              )
                         else:
                              bins = n_bins
                         ax.hist(
                              grid_col_name, 
                              data=group_df, 
                              bins=bins,
                              **extras
                         )
                         ylabel = "Frequency"
                    else:
                         ax.scatter(
                              grid_col_name,
                              grid_row_name, 
                              data=group_df, 
                              **_scatter_opts,
                              **extras
                         )
               ylabel = grid_row_name
               ax.set(
                    xlabel=grid_col_name, 
                    ylabel=ylabel,
               )
          if not dummy_group:
               ax.legend(**_legend_opts)
     return fig, axes

def figsaver(
     dir: str = ".",
     prefix: Optional[str] = None,
     dpi: int = 300, 
     format: str = 'png', 
) -> Callable[[figure.Figure, str, int, str, Optional[DataFrame]], None]:

     """Create a function to save figures in a predefined location.

     Parameters
     ----------
     dir : str, optional
          Directory to save figures. Default: ".".
     prefix : str, optional
          Prefix for filenames. Default: no prefix.
     dpi : int, optional
          Resolution of saved figures. Default: 300.
     format : str, optional
          File format of figures. Default: "png".

     Returns
     -------
     Callable
          A function taking Figure, name, and optionally a Pandas 
          DataFrame as arguments. Saves as {dir}/{prefix}{name}.{format}.
          If a DataFrame is provided, it as saved as {dir}/{prefix}{name}.csv.

     """

     def _figsave(
          fig: Figure, 
          name: str, 
          df: Optional[DataFrame] = None
     ) -> None:
          """

          """
          figname = os.path.join(output_dir, f"{prefix}{name}.{format}")
          print_err(f"Saving plot at {figname}")
          fig.savefig(
               figname, 
               dpi=dpi, 
               bbox_inches='tight',
          )
          if df is not None and isinstance(df, DataFrame):
               dataname = os.path.join(output_dir, f"{prefix}{name}.csv")
               print_err(f"Saving data at {dataname}")
               df.to_csv(dataname, index=False)
          return None
     return _figave