# -*- coding: utf-8 -*-

"""Console script for taika."""
import sys

import click

from taika.taika import run


@click.command()
@click.argument("source", )
@click.argument("dest")
def main(source, dest):
    """Read SOURCE, parse it's ReStructuredText files and write them into DEST."""
    run(source, dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
