"""Utilities for Pandas."""

from typing import Callable, Dict, Iterator, IO, Optional, Sequence, Tuple, TextIO, Union

from dataclasses import dataclass, field
import os
import sys

try:
    import pandas as pd
except ImportError:
    raise ImportError(
        """
        Pandas not installed. Try installing with pip:
            $ pip install pandas
        or reinstall carabiner with pandas:\n"
            $ pip install carabiner[pd]
        """
    )

from ..io import get_lines
from ..utils import print_err

@dataclass
class IOFormat:

    """Stores delimiters for reading and writing.

    Parameters
    ----------
    in_delim : str
        Delimiter when reading.
    out_delim : str, optional
        Delimiter when writing.
    
    """

    in_delim: str
    out_delim: Optional[str] = None
    strict: bool = True

    def __post_init__(self):
        self.out_delim = self.out_delim or self.in_delim
        if self.in_delim == '\t' and not self.strict:
            self.in_delim = r'\s+'


_FORMAT: Dict[str, Callable[[bool], IOFormat]] = {
    '.txt' : lambda strict: IOFormat('\t', strict=strict), 
    '.tsv' : lambda strict: IOFormat('\t', strict=strict), 
    '.csv' : lambda strict: IOFormat(','), 
    '.xlsx': lambda strict: IOFormat('xlsx'),
}
_FORMAT.update({
    key[1:]: value for key, value in _FORMAT.items()
})

def get_formats(allow_excel: bool = True) -> Tuple[str]:

    """List the supported table formats.

    Parameters
    ----------
    allow_excel : bool, optional
        Whether to include XLSX formats. Default: `True`.

    Returns
    -------
    tuple
        The supported table formats.

    Examples
    --------
    >>> get_formats()
    ('.txt', '.tsv', '.csv', '.xlsx', 'txt', 'tsv', 'csv', 'xlsx')
    
    """

    if allow_excel:
        return tuple(_FORMAT)
    else:
        return tuple(key for key in _FORMAT if not key.endswith('xlsx'))
    

def format2delim(
    format: str,
    default: Optional[str] = None,
    allow_excel: bool = True,
    strict: bool = True
) -> Optional[IOFormat]:
    
    r"""Return a delimiter from its format name or extension.

    Parameters
    ----------
    format : str
        Format name.
    default : str, optional
        Default delimiter to return if delimiter not supported.
    allow_excel: bool, optional
        Whether to return 'xlsx' for Excel files. If `False`, 
        returns default or `None`. Default: `True`.
    strict : bool, optional
        Whether to allow whitespace delimiter in TSV. Default: `False`.

    Returns
    -------
    IOFormat or None
        Delimiter for TSV or CSV, or "xlsx" if Excel. If not supported
        and no default, returns None

    Examples
    --------
    >>> format2delim(".csv")
    IOFormat(in_delim=',', out_delim=',', strict=True)
    >>> format2delim("tsv")
    IOFormat(in_delim='\t', out_delim='\t', strict=True)
    >>> format2delim("tsv", strict=False)
    IOFormat(in_delim='\\s+', out_delim='\t', strict=False)
    >>> format2delim(".xlsx")
    IOFormat(in_delim='xlsx', out_delim='xlsx', strict=True)
    >>> format2delim(".cool", default=".")
    IOFormat(in_delim='.', out_delim='.', strict=True)
    >>> format2delim(".cool") is None
    True

    """
    
    if default is not None:
        default_fn = lambda strict: IOFormat(default, strict=strict)
    else:
        default_fn = lambda strict: None
    delim = _FORMAT.get(format.casefold(), default_fn)(strict)

    if delim is not None:
        if delim.in_delim == 'xlsx' and not allow_excel:
            return default_fn(strict)
    
    return delim
    

def sniff(
    file: Union[str, IO],
    default: Optional[str] = None,
    allow_excel: bool = True,
    strict: bool = True
) -> Optional[IOFormat]:

    r"""Identify the delimiter of a file from its extension.

    Parameters
    ----------
    file : str or file-like
        Input path to file or a file-like object.
    default : str, optional
        Default delimiter to return if delimiter not supported.
    allow_excel: bool, optional
        Whether to return 'xlsx' for Excel files. If `False`, 
        returns default or `None`. Default: `True`.
    strict : bool, optional
        Whether to allow whitespace delimiter in TSV. Default: `False`.

    Returns
    -------
    IOFormat or None
        Delimiter for TSV or CSV, or "xlsx" if Excel. If not supported
        and no default, returns None

    Examples
    --------
    >>> sniff("test.csv")
    IOFormat(in_delim=',', out_delim=',', strict=True)
    >>> sniff("test.tsv")
    IOFormat(in_delim='\t', out_delim='\t', strict=True)
    >>> sniff("test.tsv", strict=False)
    IOFormat(in_delim='\\s+', out_delim='\t', strict=False)
    >>> sniff("test.xlsx")
    IOFormat(in_delim='xlsx', out_delim='xlsx', strict=True)
    >>> sniff("test.cool", default=".")
    IOFormat(in_delim='.', out_delim='.', strict=True)
    >>> sniff("test.cool") is None
    True
    >>> sniff("test.xlsx")
    IOFormat(in_delim='xlsx', out_delim='xlsx', strict=True)
    >>> sniff("test.xlsx", allow_excel=False) is None
    True
    >>> sniff("test.tsv.gz")
    IOFormat(in_delim='\t', out_delim='\t', strict=True)

    """

    try:
        filename = file.name
    except AttributeError:  ## probably str
        filename = file

    if filename.endswith('.gz') or filename.endswith('.gzip'):
        new_filename, _ = os.path.splitext(filename)
        return sniff(new_filename, default, allow_excel)
    else:
        _, ext = os.path.splitext(filename)
    return format2delim(
        ext.casefold(), 
        default=default, 
        allow_excel=allow_excel,
        strict=strict,
    )


def resolve_delim(
    file: Union[str, IO],
    format: Optional[str] = None,
    default: Optional[str] = None,
    allow_excel: bool = True
) -> Optional[IOFormat]:
    
    r"""Identify the delimiter of a file.
    
    Uses the file extension, unless an explicit format is provided.

    Parameters
    ----------
    file : str or file-like
        File whose delimiter should be identified.
    format : str, optional
        Override the file extension to return a format.
    default : str, optional
        Provide this default if the extension cannot be identified,
        otherwise return `None`.
    allow_excel : bool, optional
        Whether to return 'xlsx' for Excel files. If `False`, 
        returns default or `None`. Default: `True`.

    Returns
    -------
    IOFormat or None
        Delimiter for TSV or CSV, or "xlsx" if Excel. If not supported
        and no default, returns None

    Examples
    --------
    >>> resolve_delim("test.tsv", format="csv")
    IOFormat(in_delim=',', out_delim=',', strict=True)
    >>> resolve_delim("test.tsv", format="tsv")
    IOFormat(in_delim='\t', out_delim='\t', strict=True)
    >>> resolve_delim("test.cool") is None
    True
    >>> resolve_delim("test.cool", default="\t")
    IOFormat(in_delim='\t', out_delim='\t', strict=True)

    """
    
    if format is None:
        return sniff(file, default=default, allow_excel=allow_excel)
    else:
        return format2delim(format, default=default)


def read_csv(
    filename: Union[str, TextIO], 
    rows: Optional[Union[int, Sequence[int]]] = None, 
    progress: bool = True,
    *args, **kwargs
) -> pd.DataFrame:
    
    """Read a delimited file, optionally GZIPped, optionally only specific rows.
    
    Provides a progress bar by default. Addtional arguments are passed to `pd.read_csv`.

    Parameters
    ----------
    filename : str
        Path of file to read. Optionally GZIP compressed.
    rows : list of int, optional
        Rows to read. If `None` (default), read all rows.
    progress : bool
        Whether to display a progress bar. Default: `True`.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame of the input file.

    """
    
    if rows is not None:
        rows = {0} | {row + 1 for row in rows}
        nrows = len(rows)
    else:
        nrows = 'all'

    if progress:
        print_err(f"Reading {nrows} rows from {filename}...")
    
    lines = get_lines(filename, 
                      lines=rows, 
                      progress=progress)
    return pd.read_csv(lines, *args, **kwargs)
    

def read_table(
    file: Union[str, IO],
    format: Optional[str] = None,
    progress: bool = False,
    sheet_name: Optional[Union[str, int, list]] = None,
    chunksize: Optional[int] = None,
    *args, **kwargs
) -> Union[pd.DataFrame, Iterator[pd.DataFrame]]:

    """Universal reader of tabular data files.

    Addtional arguments are passed to `read_csv` or `pd.read_excel`. If `chunksize` is
    provided, returns a iterator of chunks which is lazy for non-Excel files but greedy for 
    Excel files. Otherwise returns a DataFrame.

    Parameters
    ----------
    filename : str
        Path of file to read in CSV, TSV or Excel format. Optionally GZIP compressed.
    format : str
        Format name. Default: infer from filename
    sheet_name : str, int or list, optional
        If reading an XLSX file, which sheets to read. Default: read all sheets.

    Returns
    -------
    pd.DataFrame or iterator of pd.DataFrame
        Pandas DataFrame of the input file.
    
    """
    
    delimiter = resolve_delim(
        file, 
        format, 
        default='\t',
    )

    if delimiter.in_delim != 'xlsx':
        return read_csv(
            file, 
            sep=delimiter.in_delim,
            encoding='unicode_escape',
            progress=progress,
            chunksize=chunksize,
            *args, **kwargs
        )
    else:
        df = pd.read_excel(
            file.name, 
            engine='openpyxl',
            sheet_name=sheet_name,
            *args, **kwargs
        )
        if chunksize is None:
            return df
        else:
            return (
                df.iloc[i:(i + chunksize)] for i in range(0, df.shape[0], chunksize)
            )
        
    
def write_stream(
    df: pd.DataFrame, 
    output: Union[TextIO, str] = sys.stdout,
    format: Optional[str] = None,
    *args, **kwargs
) -> None:
    
    """Write a Pandas DataFrame to a file or stdout.
    
    Similar to pd.write_csv() but excludes the index by default and writes to 
    stdout by default with support for truncating output without complaining 
    about broken pipes.

    Addtional arguments are passed to `pd.write_csv`.

    Parameters
    ----------
    df : pd.DataFrame
        Input Pandas DataFrame to write out.
    output : str, optional
        Path to output filename. Default: stdout.
    format : str
        Format name. Default: infer from filename
    
    Returns
    -------
    None
    
    """
    
    delimiter = resolve_delim(
        output, 
        format, 
        allow_excel=False,
        default='\t',
    )
    try:
        df.to_csv(
            output,
            sep=delimiter.out_delim,
            index=False,
            *args, **kwargs
        )
    except BrokenPipeError:
        sys.exit(0)
    return None