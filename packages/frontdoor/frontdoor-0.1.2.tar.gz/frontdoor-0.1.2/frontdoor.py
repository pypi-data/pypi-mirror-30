"""
Front Door
----------

This simple module aids in the creation of "front door" scripts, which can
help organize automated scripts and reduce the need for overly verbose docs.
The idea is you can copy this file into your repository and import it from a
Python script.

A front door script generally accepts a series of options which defer to some
other process call to do work of some kind. There is an example in the Front
Door repo (located at https://github.com/TimSimpson/frontdoor) of what this
looks like, but in short, it lets common commands that you might want to tell
someone about in documentation exist in a script that people can run instead.

License
-------
Written in 2017 by Tim Simpson

To the extent possible under law, the author(s) have dedicated all copyright
and related and neighboring rights to this software to the public domain
worldwide. This software is distributed without any warranty.

You should have received a copy of the CC0 Public Domain Dedication along with
this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
"""
from __future__ import print_function

import os


ROOT = os.path.dirname(os.path.realpath(__file__))


if False:  # This works thanks to MyPy's Python 2 compatibility mode.
    import typing as t  # NOQA


def from_root(path):
    # type: (str) -> str
    """Returns a path relative to the root directory."""
    if os.name == 'nt':
        path = path.replace('/', '\\')
    return os.path.join(ROOT, path)


class CommandRegistry(object):
    """
    Organizes commands, which are simple functions associated with a name and
    some documentation.
    """

    def __init__(self, name):
        # type: (str) -> None
        self.commands = {}  # type: dict
        self.name = name
        # Adds a help function - this can be overwritten.
        self.decorate('help')(lambda args: self.help(args))

    def decorate(self, name, desc='', help=None):
        # type: (t.Union[str, t.List[str]], str, t.Optional[str]) -> t.Callable
        """Decorates a function to make it a command."""
        def cb(func):
            # type: (t.Callable) -> t.Callable
            if isinstance(name, str):
                names = [name]
                visible_name = name
            else:
                names = name
                visible_name = ','.join(names)

            for index, key in enumerate(names):
                self.commands[key] = {
                    'fn': func,
                    'desc': desc,
                    'help': help,
                    'show': index == 0,
                    'visible_name': visible_name,
                }
            return func

        return cb

    def dispatch(self, args):
        # type: (t.List[str]) -> int
        """Pass in sys.argv or something equivalent."""
        if len(args) < 1:
            print("Expected argument.")
            self.help(args)
            return 1

        command = args[0]
        rest = args[1:]

        try:
            fn = self.commands[command]
        except KeyError:
            if self.name:
                print('{} knows not of command "{}".'
                      .format(self.name, command))
            else:
                print('I know not of this command "{}".'.format(command))
            print()
            self.help([])
            return 1
        exit_code = fn['fn'](rest)
        if exit_code is None:
            return 0
        return exit_code

    def help(self, args):
        # type: (t.List[str]) -> int
        """Offers help."""
        bad_command = False
        if len(args) > 0:
            name = args[0]
            command = self.commands.get(name)
            if command:
                print(name)
                if command['desc']:
                    print("\t{}".format(command['desc']))
                print()
                if command['help']:
                    print(command['help'])
                    print()
                return 0
            else:
                bad_command = True
                print('Unknown command "{}".'.format(name))

        # Print out all commands

        if self.name:
            print('Available options for {}:'.format(self.name))
        else:
            print('Available options:')
        max_name = max(len(values['visible_name'])
                       for values in self.commands.values())
        max_spacing = max(max_name, 16)

        for value in sorted(self.commands.values(),
                            key=lambda v: v['visible_name']):
            if value['show']:
                print("    {}{}{}".format(
                    value['visible_name'],
                    ' ' * (max_spacing - len(value['visible_name'])),
                    value['desc']).rstrip())

        return 0 if not bad_command else 1
