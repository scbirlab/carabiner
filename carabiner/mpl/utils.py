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
    from matplotlib import axes, cycler, figure, rcParams, legend
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
     square: bool = False,
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
     square: bool
          Whether to force panels to be square. Default: `True`.

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
     all_axes = fig.axes
     if square:
          for ax in all_axes:
               ax.set(aspect="equal")
     if sharex: 
          for ax in all_axes:
               ax.xaxis.set_tick_params(labelbottom=True)
     if sharey:
          for ax in all_axes:
               ax.yaxis.set_tick_params(labelleft=True)
     return fig, axes


def add_legend(
     ax: axes.Axes,
     **kwargs
) -> legend.Legend:

     """Add a legend to the right of a Matplotlib plotting axis.

     Uses a sensible default for putting the legend out of the way. Keyword arguments 
     override `loc` and `bbox_to_anchor`, and additional arguments are passed to 
     `matplotlib.axes.Axes.legend()`.

     Parameters
     ----------
     ax : matplotlib.axes.Axes
          Axes to add a legend to.

     Returns
     -------
     matplotlib.legend.Legend

     """
     default_opts = {
          "loc": 'center left',
          "bbox_to_anchor": (1, .5)
     }
     default_opts.update(kwargs)
     return ax.legend(**default_opts)


def scattergrid(
     df: DataFrame, 
     grid_columns: Union[str, Iterable[str]], 
     grid_rows: Optional[Union[str, Iterable[str]]] = None, 
     grouping: Optional[Union[str, Iterable[str]]] = None,
     log: Optional[Union[str, Iterable[str]]] = None,
     n_bins: int = 40,
     scatter_opts: Optional[Mapping[str, Any]] = None,
     hist_opts: Optional[Mapping[str, Any]] = None,
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
     hist_opts : dict, optional
          Extra keyword arguments to pass to the Matplotlib histogram plots.
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

     _scatter_opts = {"s": 3.}
     _scatter_opts.update(scatter_opts or {})
     _hist_opts = {"alpha": .7} if not dummy_group else {}
     _hist_opts.update(hist_opts or {})
     _legend_opts = {}
     _legend_opts.update(legend_opts or {})

     fig, axes = grid(
          nrow=len(grid_rows), 
          ncol=len(grid_columns),
          *args, **kwargs
     )
     for axrow, grid_row_name in zip(tqdm(axes), grid_rows):
          for ax, grid_col_name in zip(axrow, grid_columns):
               make_histogram = grid_row_name == grid_col_name
               xscale = "log" if grid_col_name in log else "linear"
               yscale = "log" if (grid_row_name in log and not make_histogram) else "linear"
               ylabel = grid_row_name if not make_histogram else "Frequency"
               for group_name, group_df in df:
                    labels = {"label": ":".join(map(str, group_name))} if not dummy_group else {}
                    if make_histogram:
                         if xscale == "log":
                              values = group_df.query(f"`{grid_col_name}` > 0")[grid_col_name].values
                              values = values[np.isfinite(values)]
                              if values.size > 0:
                                   values_min, values_max = values.min(), values.max()
                                   if values_min == values_max:
                                        hist_max = values_min + 1.
                                   else:
                                        hist_max = values_max
                                   bins = np.geomspace(
                                        values_min, 
                                        hist_max, 
                                        num=n_bins,
                                   )
                              else:
                                  continue 
                         else:
                              bins = n_bins
                         try:
                              ax.hist(
                                   grid_col_name, 
                                   data=group_df, 
                                   bins=bins,
                                   **_hist_opts,
                                   **labels,
                              )
                         except ValueError as e:  # Usually some problem with value ranges, but shouldn't prevent plotting
                              print_err(e)
                    else:
                         ax.scatter(
                              grid_col_name,
                              grid_row_name, 
                              data=group_df, 
                              **_scatter_opts,
                              **labels,
                         )
               ax.set(
                    xlabel=grid_col_name, 
                    ylabel=ylabel,
                    xscale=xscale,
                    yscale=yscale,
               )
          if not dummy_group:
               add_legend(ax, **_legend_opts)
     return fig, axes


def figsaver(
     output_dir: str = ".",
     prefix: Optional[str] = None,
     dpi: int = 300, 
     format: str = 'png', 
) -> Callable[[figure.Figure, str, int, str, Optional[DataFrame]], None]:

     """Create a function to save figures in a predefined location.

     Parameters
     ----------
     output_dir : str, optional
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

     prefix = prefix or ""
     if not os.path.exists(output_dir):
          os.mkdir(output_dir)

     def _figsave(
          fig: figure.Figure, 
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

     return _figsave