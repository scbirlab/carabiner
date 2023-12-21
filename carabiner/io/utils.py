"""Utilities for IO."""

from typing import Callable, Generator, Sequence, TextIO, Union
from functools import partial
import gzip
from io import StringIO

from tqdm.auto import tqdm

from ..utils import print_err, tenumerate

def _enumerate_file(filename: str, 
                    opener: Union[Callable[[str], TextIO], 
                                  None] = None, 
                    progress: bool = True,
                    *args, **kwargs) -> Generator:
    
    if opener is None:
        if filename.endswith('.gz'):
            opener = partial(gzip.open, mode='rt')
        else:
            opener = open
    
    enumerator = tenumerate if progress else enumerate

    with opener(filename, *args, **kwargs) as f:

        return enumerator(f)
    

def count_lines(filename: str, 
                progress: bool = True,
                *args, **kwargs) -> int:
    
    """Count lines in a file, optionally gzipped.
    
    
    """
    
    if progress:
        print_err(f"Counting lines in {filename}...")

    for i, _ in _enumerate_file(filename, 
                                progress=progress, 
                                *args, **kwargs):

            pass
                
    return i + 1


def get_lines(filename: str,
              lines: Sequence[int],
              progress: bool = True,
              outfile: Union[TextIO, None] = None,
              *args, **kwargs) -> TextIO:
    
    """Extract lines from a file by number.
    
    """

    outfile = outfile or StringIO()
    
    line_numbers_to_keep = set(lines)
    nlines_to_read = max(line_numbers_to_keep)

    for i, line in _enumerate_file(filename, 
                                   progress=progress, 
                                   *args, **kwargs):

        if i in line_numbers_to_keep:

            outfile.write(line)

        if i > nlines_to_read:

            break

    return outfile