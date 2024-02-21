"""Utilities for constructing command-line interfaces."""

from typing import Callable, Iterable, Mapping, Optional

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from collections import namedtuple
from dataclasses import asdict, dataclass, field
from datetime import timedelta
from functools import wraps
import textwrap
from time import time

from .decorators import decorator_with_params
from .utils import print_err, pprint_dict

_ADD_ARGUMENT_PARAMS = ('name', 'action', 'nargs', 'const', 
                        'default', 'type', 'choices', 'required', 
                        'help', 'metavar', 'dest')

TMainFunction = Callable[[Namespace], None]

@decorator_with_params
def clicommand(main: TMainFunction,
               message: Optional[str] = None, 
               name: Optional[str] = None) -> TMainFunction:
    
    """Convert a function to act informatively as the main function in a CLI app.

    Parameters
    ----------
    message : str, optional
        Message to prepend to reporting of parameters.
    name: str, optional
        Name of the app.

    Returns
    -------
    Callable
        Decorator for function to be used as a main function in a CLI app.
    
    """
    
    message = message or "Processing with the following parameters"
    name = name or "process"
    
    @wraps(main)
    def _clicommand(args: Namespace) -> None:


        start_time = time()

        pprint_dict(args,
                    message="🚀 " + message)

        main(args)

        process_time = time() - start_time

        print_err(f'⏰ Completed {name} in {timedelta(seconds=process_time)}')

        return None

    return _clicommand
    

@dataclass
class BaseCLIOption:

    """

    """

    args: Optional[Iterable] = field(default_factory=list)
    kwargs: Optional[Mapping] = field(default_factory=dict)

    def __post_init__(self):

        if 'required' in self.kwargs and 'default' in self.kwargs:

            if self.kwargs['default'] is not None and self.kwargs['required']:

                raise AttributeError(f"Cannot set both {self.kwargs['required']=} and "
                                     f"{self.kwargs['default']=} for CLIOption.")

        if 'help' in self.kwargs:

            if ('default' in self.kwargs and 
                ' Default: ' not in self.kwargs['help'] and 
                self.kwargs['default'] is not None):

                self.kwargs['help'] += ' Default: "{}".'.format(self.kwargs['default'])

            elif 'required' in self.kwargs and self.kwargs['required']:

                self.kwargs['help'] += ' Required.'


class CLIOption(BaseCLIOption):

    """

    """

    def __init__(self, *args, **kwargs):

        super().__init__(args=args, 
                         kwargs=kwargs)

    def replace(self, **kwargs):

        _copy = BaseCLIOption(**asdict(self))

        for key, value in kwargs.items():

            _copy.kwargs[key] = value

        return _copy


@dataclass
class CLICommand:

    """

    """

    name: str
    description: Optional[str] = None
    options: Iterable[CLIOption] = field(default_factory=list)
    main: Optional[Callable] = None


@dataclass
class CLIApp:

    """

    """

    name: str
    version: str
    description: Optional[str] = None
    commands: Iterable[CLICommand] = field(default_factory=list)
    _parser: ArgumentParser = field(init=False)
    _subcommands: Iterable = field(init=False, default_factory=list)
    
    def __post_init__(self):

        self._parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                                      description=textwrap.dedent(self.description))

        if len(self.commands) > 0:

            subcommands =  self._parser.add_subparsers(title='Sub-commands', 
                                                       dest='subcommand',
                                                       help='Use these commands to specify the tool you want to use.')
        
            for command in self.commands:

                this_command = subcommands.add_parser(command.name, 
                                                      help=command.description)
                this_command.set_defaults(func=command.main)

                for option in command.options:

                    this_command.add_argument(*option.args, **option.kwargs)

                self._subcommands.append(this_command)

        self._args = self._parser.parse_args()

    def run(self):

        """

        """

        return self._args.func(self._args)

