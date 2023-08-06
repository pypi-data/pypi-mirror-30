#!/usr/bin/env python3

import argparse
import json
import logging
import traceback

# This feels janky, but I'm lazy and it makes the code a bit easier.
class Argument(object):
    # name or flags - Either a name or a list of option strings, e.g. foo or -f, --foo.
    # action - The basic type of action to be taken when this argument is encountered at the command line.
    # nargs - The number of command-line arguments that should be consumed.
    # const - A constant value required by some action and nargs selections.
    # default - The value produced if the argument is absent from the command line.
    # type - The type to which the command-line argument should be converted.
    # choices - A container of the allowable values for the argument.
    # required - Whether or not the command-line option may be omitted (optionals only).
    # help - A brief description of what the argument does.
    # metavar - A name for the argument in usage messages.
    # dest - The name of the attribute to be added to the object returned by parse_args().
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        pass
    pass

class CLIDispatcher(object):
    description = ''

    shared_args = []

    operation_info={}

    @classmethod
    def execute(cls, action, **kwargs):
        raise RuntimeError('Each subclass must override this!')

    @classmethod
    def get_argument_parser(cls):
        parser = argparse.ArgumentParser(description=cls.description)
        operations = parser.add_mutually_exclusive_group(required=True)

        for operation in cls.operation_info.keys():
            op = cls.operation_info[operation]
            operation_cli = '--{0}'.format(operation)
            # operation_cli = '--{0}'.format(operation.replace('_','-'))
            # operations.add_argument(operation_cli, action='store_true', help='Operation: {0}'.format(op['help']))
            if op.get('initial', None):
                operations.add_argument('-{0}'.format(op['initial']), operation_cli, action='store_true', help='Operation: {0}'.format(op['help']))
            else:
                operations.add_argument(operation_cli, action='store_true', help='Operation: {0}'.format(op['help']))
        for arg in cls.shared_args:
            parser.add_argument(*arg.args, **arg.kwargs)
        return parser

    @classmethod
    def handle_args(cls, args):
        operation = None
        kwargs = {p[0]:p[1] for p in args._get_kwargs()}
        for key in kwargs:
            if key.replace("_","-") in cls.operation_info and kwargs[key]:
                operation = key.replace("-","_")
        verbosity = kwargs["verbosity"]
        if verbosity >= 2:
            logging.basicConfig(level=logging.DEBUG)
        elif verbosity >= 1:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARN)
        try:
            cls.execute(operation, **kwargs)
        except:
            traceback.print_exc()
            exit(1)

    @classmethod
    def do_stuff(cls):
        parser = cls.get_argument_parser()
        args = parser.parse_args()
        cls.handle_args(args)
