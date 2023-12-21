"""Utilities for Pandas."""

from typing import Sequence, Union

import pandas as pd

from ..io import count_lines, get_lines
from ..utils import print_err


def read_csv(filename: str, 
             rows: Union[Sequence[int], None] = None, 
             progress: bool = True,
             *args, **kwargs):
    
    """Read a delimited file, optionally only specific rows.
    
    Provides a progress bar by default.

    """
    
    rows = rows or range(count_lines(filename, progress=progress) - 1)

    if progress:

        print_err(f"Reading {len(rows)} from {filename}...")
    
    lines = get_lines(filename, 
                      lines={0} | {row + 1 for row in rows}, 
                      progress=progress)
        
    return pd.read_csv(lines, *args, **kwargs)
    