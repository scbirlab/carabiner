"""Command-line interface for carabiner."""

# from typing import Sequence
from argparse import FileType, Namespace
import sys

from . import __version__
from .cliutils import clicommand, CLIOption, CLICommand, CLIApp

@clicommand(message='Parsed arguments', name='cbnr')
def _main(args: Namespace) -> None:
    
    return None


def main() -> None:

    inputs = CLIOption('inputs',
                        type=str,
                        default=[],
                        nargs='*',
                        help='')
    output = CLIOption('--output', '-o', 
                        type=FileType('w'),
                        default=sys.stdout,
                        help='Output file. Default: STDOUT')
    formatting = CLIOption('--format', '-f', 
                           type=str,
                           default='TSV',
                           choices=['TSV', 'CSV', 'tsv', 'csv'],
                           help='Format of files. Default: %(default)s')

    test = CLICommand("test",
                      description="Test CLI subcommand using Carabiner utilities.",
                      options=[inputs, output, formatting],
                      main=_main)

    app = CLIApp("Carabiner", 
                 version=__version__,
                 description="Test CLI app using Carabiner utilities.",
                 commands=[test])

    app.run()

    return None


if __name__ == '__main__':

    main()

