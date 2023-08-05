# -*- coding: utf-8 -*-

"""Console script for chucknorrisfacts."""
import sys
import click
from chucknorrisfacts.chucknorrisfacts import cnfacts


@click.command()
def main(args=None):
    """Console script for chucknorrisfacts."""
    #click.echo("Replace this message by putting your code into "
    #           "chucknorrisfacts.cli.main")
    #click.echo("See click documentation at http://click.pocoo.org/")
    cnfacts()
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
