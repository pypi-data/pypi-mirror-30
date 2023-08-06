# (C) Copyright 2016 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import sys

import click


allow_assume_yes = click.option(
    "assume_yes", "-y", "--yes", default=False, is_flag=True,
    help=("If given, always assume yes to every prompt, "
          "and run non-interactively."),
)


def request_confirmation(msg, default=False):
    """ Request confirmation from the user.
    """
    if not click.confirm(msg, default=default):
        sys.exit(0)
