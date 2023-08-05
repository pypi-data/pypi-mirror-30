"""Holds the Command base class and its necesseray metaclasses and helper
"""

class CommandMeta(type):
    """Meta class for the Command class to set certain class properties
    """
    @property
    def command(self):
        """get the command string of the command class
        :returns: the command string to invoke the command
        """
        return self._command

    @property
    def description(self):
        """get the command description
        :returns: the description string of the command
        """
        return self._description

    @property
    def hidden(self):
        """returns if the command is hidden or visible
        :returns: True if the command is hidden, False else
        """
        return self._hide


class Command(metaclass=CommandMeta):
    """A command that is executed by the Subcommand class
    :var str _command: the command string to invoke this command
    :var str _description: short description of the command. used for help text
    :var boolean _hide: hide the command from the help text
    """
    _command = ''
    _description = ''
    _hide = False

    @staticmethod
    def dispatch(self, *args, **kwargs):
        """command entrypoint. dispatches all arguments for this custom command
        """
        raise NotImplementedError('Method must be implemented by custom command class')
