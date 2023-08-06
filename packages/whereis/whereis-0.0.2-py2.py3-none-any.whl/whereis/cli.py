# -*- coding: utf-8 -*-

"""Console script for whereis."""

import os
import click
import subprocess


def where_is_executable(app):
    """Return a list of locations a given application.

    Relies on the `where` command in Windows and the `which` command in Unix.

    Parameters
    ----------
    app : str
        Can be any application on the system path e.g. java.

    Returns
    -------
    result : list
        A list of locations where applications is installed.

    Useage
    ------
    >>>where_is_executable('javac')
    'C:\\Program Files\\Java\\jdk1.8.0_162\\bin\\javac.exe'
    """
    result = []

    command = 'where'
    if os.name != "nt":# Windows
        command = 'which'

    try:
        result = subprocess.check_output("{} {}".format(command, app))

    except CalledProcessError as err:
        print("Application {} not found.".format(err))
        return retun

    result = result.decode().splitlines()
    result = [line for line in result if len(line)]
    return result


# import sys
import click


@click.command()
def main(args=None):
    where_is_executable(args)

    """Console script for whereis."""
    click.echo("Replace this message by putting your code into "
               "whereis.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
