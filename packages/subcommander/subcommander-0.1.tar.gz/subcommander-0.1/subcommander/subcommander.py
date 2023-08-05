"""Subcommander class and its necessary helper classes
"""
import argparse
import sys

from command import Command

class DuplicateCommandError(Exception):
    """Error if duplicate commands are detected
    """
    def __init__(self, message, key):
        """
        """
        super(DuplicateCommandError, self).__init__(message)
        self.key = key


def build_command_dict(default, extensions):
    """merge the default commands and extended commands

    :param [Command] default: list with default command classes
    :param [Command] extensions: list with extended command classes
    :raises DuplicateCommandError: if any command key is duplicated
    :returns: dictionary with commands ins form 'command-key': CommandClass
    """
    command_dict = {}

    # filter duplicate commands from default command list
    for command in default:
        try:
            command_dict[command.command] = command
        except KeyError:
            raise DuplicateCommandError('Duplicate Key detected', command.command)

    # add additional commands and check for duplicates
    for command in extensions:
        if not command in default:
            try:
                command_dict[command.command] = command
            except KeyError:
                raise DuplicateCommandError('Duplicate Key detected', command.command)
        else:
            raise DuplicateCommandError('Duplicate Key detected', command.command)

    return command_dict


class ArgumentParser(object):
    """Parse commandline arguments utilizing an inner argparse.ArgumentParser object
    """
    def __init__(self, subcommander):
        """create the inner ArgumentParser and setup the help text
        :param Subcommander subcommander: the outer Subcommander to get all available commands
        """
        # inner argumentparser
        self._subparser = argparse.ArgumentParser()
        # perpare help text for the available subcommands
        positional_args = ''
        for cmd_key, cmd_obj in subcommander._commands.items():
            positional_args = positional_args + '    {}    {}\n'.format(
                                cmd_obj.command, cmd_obj.description)
        # build usage text
        self._usage = (
            '{} ({})\n'
            '\n'
            'usage: {} [-h] <command> [<args>] \n'
            '\n'
            'positional arguments:\n'
            '{}'
            '\n'
            'optional arguments:\n'
            '   -h, --help      show this help message and exit'
            '').format(subcommander._name, subcommander._version, subcommander._cmd, positional_args)
        # overwrite the inner argumentparser help method to print the custom usage build above
        setattr(self._subparser, 'format_help', lambda: print(self._usage))


    def add_argument(self, *args, **kwargs):
        """wrapper to forward to inner ArgumentParser add_argument method
        """
        return self._subparser.add_argument(*args, **kwargs)

    def parse_args(self, *args, **kwargs):
        """wrapper to forward to inner ArgumentParser parse_args method
        """
        return self._subparser.parse_args(*args, **kwargs)


class Subcommander(object):
    """Subcommander class that takes a list of subcommands to execute
    :param [Command] _default_commands: a list of default commands. used if further subclassing is necessary
    :param str _name: the name of the application
    :param str _cmd: the command used to execute the app from the commandline
    :param str _version: version of the application
    """
    _default_commands = []
    _name = 'Subcommander'
    _cmd = 'subcmd'
    _version = '1.0'

    def __init__(self, extensions=None):
        """setup the argument dispatching and add extended commands if provided
        :param [Command] extensions: a list of optional Commands
        """
        # merge default commands and custom app commands
        if extensions is not None:
            try:
                self._commands = build_command_dict(self.__class__._default_commands, extensions)
            except DuplicateCommandError as err:
                print('Command Error!'
                    'Command duplication detected! Could not initialize custom commands.'
                    'Command \'{}\' already exists!'.format(err.key))
                exit(1)
        else:
            self._commands = build_command_dict(self.__class__._default_commands, [])

        # dispatch commands
        parser = ArgumentParser(self)
        parser.add_argument('command', help='the command to run')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        arguments = parser.parse_args(sys.argv[1:2])
        if not arguments.command in self._commands:
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        self._commands[arguments.command]()(sys.argv[2:])
