# Copyright 2018 Canonical Ltd.
# Licensed under the LGPLv3, see LICENCE.txt file for details.

"""Main entry point for the application commands."""

from functools import partial
import sys

from . import (
    _exceptions,
    _fsteal,
)


def main(command, args=None):
    """Set up and run the given command.

    The provided command is an object implementing the following interface:
        - setup(args) -> namespace:
          it parses the given args (which could be None) and returns the
          resulting argparse.Namespace object;
        - run(namespace):
          it executes the command receiving the namespace and possibly raising
          firestealer.FirestealerError (or subclasses).
    """
    namespace = command.setup(args)
    try:
        command.run(namespace)
    except KeyboardInterrupt:
        print('exiting')
        sys.exit(1)
    except _exceptions.FirestealerError as err:
        sys.exit(err)


fsteal = partial(main, _fsteal)
