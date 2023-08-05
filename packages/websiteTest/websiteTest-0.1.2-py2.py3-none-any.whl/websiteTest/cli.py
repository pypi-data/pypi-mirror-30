# -*- coding: utf-8 -*-

"""Console script for websiteTest."""
import sys
import click
from websiteTest.websiteTest import tester


@click.command()

def main(url, function, template_path, template_name, check_path, check_name):
    """Console script for websiteTest."""
    click.echo("Replace this message by putting your code into "
               "arepa.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
