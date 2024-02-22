"""Utilities for IO."""

from typing import Callable, Iterator, Optional, Sequence, Tuple, Union
from functools import partial
import gzip
from io import StringIO, TextIOWrapper
import math
from tempfile import _TemporaryFileWrapper

from ..itertools import tenumerate
from ..utils import print_err

def _enumerate_file(filename: str, 
                    opener: Optional[Callable[[str], TextIOWrapper]] = None, 
                    progress: bool = True,
                    total: Optional[int] = None,
                    *args, **kwargs) -> Iterator[Tuple[int, str]]:
    
    if isinstance(filename, str):
        if opener is None:
            if filename.endswith('.gz'):
                opener = partial(gzip.open, mode='rt')
            else:
                opener = open
        
        handle = opener(filename, *args, **kwargs)
    elif isinstance(filename, TextIOWrapper) or isinstance(filename, _TemporaryFileWrapper):
        handle = filename
    else:
        raise IOError(f"Object {filename} is not a string (path) or a file-like object.")
    
    enumerator = (partial(tenumerate, total=total) if progress 
                  else enumerate)

    return enumerator(handle)
    

def count_lines(filename: Union[TextIOWrapper, str], 
                progress: bool = True,
                *args, **kwargs) -> int:
    
    """Count lines in a file, optionally gzipped.

    Provides a progress bar by default.
    
    Parameters
    ----------
    filename : str
        Path of file to read. Optionally GZIP compressed.
    progress : bool
        Whether to display a progress bar. Default `True`.

    Returns
    -------
    int
        Number of lines in input file.
    
    """
    
    if progress:
        print_err(f"Counting lines in {filename}...")

    for i, _ in _enumerate_file(filename, 
                                progress=progress, 
                                *args, **kwargs):

            pass
                
    return i + 1


def get_lines(filename: Union[TextIOWrapper, str],
              lines: Optional[Union[int, Sequence[int]]] = None,
              progress: bool = True,
              outfile: Optional[TextIOWrapper] = None,
              *args, **kwargs) -> Union[TextIOWrapper, StringIO]:
    
    """Extract lines from a file, optionally GZIPped, by line number.

    Provides a progress bar by default.

    Parameters
    ----------
    filename : str or file-like
        Path of file to read, or a file-like object. Optionally GZIP compressed.
    lines : list of int, optional
        Rows to read. If `None` (default), read all rows.
    progress : bool
        Whether to display a progress bar. Default `True`.
    outfile : file-like, optional
        Open file handle for output.

    Returns
    -------
    TextIOWrapper or StringIO
        File-like object containing lines from the input file.
    
    """

    outfile = outfile or StringIO()
    
    if lines is not None:
        
        if isinstance(lines, int):
            lines = range(lines)

        line_numbers_to_keep = set(lines)
        nlines_to_read = max(line_numbers_to_keep)

    else:

        line_numbers_to_keep = set()
        nlines_to_read = math.inf

    for i, line in _enumerate_file(filename, 
                                   progress=progress, 
                                   total=nlines_to_read,
                                   *args, **kwargs):

        if (lines is None) or (i in line_numbers_to_keep):

            print(line, file=outfile, end='')

        if i > nlines_to_read:

            break

    outfile.seek(0)  ## Essential to return to start of file 

    return outfile