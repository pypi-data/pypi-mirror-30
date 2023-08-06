Front Door
==========

|Build Status| |Build status|

This simple module aids in the creation of "front door" scripts, which
can help organize automated scripts and reduce the need for overly
verbose docs. The idea is you can copy ``frontdoor.py`` into your
repository to make it easy to bootstrap a front door script of your own
(the other files in this repo are just examples that illustrate how
frontdoor.py is used).

A front door script is a command which accepts a series of options which
themselves may defer to other commands or processes which do work of
some kind.

So say you have a project that has unit tests, integration tests, and
deployment scripts. Typically you'd include a series of scripts, along
with documentation on what scripts do what and how. What makes a front
door script different is that you just document it's available and users
can find other options by jumping in and exploring it themselves. The
end result feels a little like playing an interactive fiction computer
game such as Zork.

This solves a different use case from argparse as argparse is more about
creating robust, single purpose tools that can be invoked in flexible
ways, where as Front Door is about creating scripts that more easily
accept positional arguments and can defer to other commands. It's also
extremely simple and designed to be copy and pasted.

.. |Build Status| image:: https://travis-ci.org/TimSimpson/frontdoor.svg?branch=mas
   :target: https://travis-ci.org/TimSimpson/frontdoor
.. |Build status| image:: https://ci.appveyor.com/api/projects/status/dfwa2mv8wskx6x6r?svg=true
   :target: https://ci.appveyor.com/project/TimSimpson/frontdoor
