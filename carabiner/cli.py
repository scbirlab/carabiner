"""Command-line interface for carabiner."""

# from typing import Sequence
import argparse
import sys
import textwrap

from .utils import pprint_dict


def _main(args: argparse.Namespace) -> None:

    pprint_dict(vars(args), 
                'Parsed arguments')
    
    return None


def main() -> None:

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent(''''''))

    parser.set_defaults(func=_main)

    parser.add_argument('inputs',
                        type=str,
                        default=[],
                        nargs='*',
                        help='')
    parser.add_argument('--format', '-f', 
                        type=str,
                        default='TSV',
                        choices=['TSV', 'CSV', 'tsv', 'csv'],
                        help='Format of files. Default: %(default)s')
    parser.add_argument('--output', '-o', 
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='Output file. Default: STDOUT')
    
    args = parser.parse_args()
    args.func(args)

    return None


if __name__ == '__main__':

    main()

