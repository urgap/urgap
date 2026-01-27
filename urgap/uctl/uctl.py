"""Uctl module of urgap2.

This is the main CLI entrypoint and command group dispatcher for urgap2.
"""

import click

import urgap

from urgap.uctl.describe import describe
from urgap.uctl.info import info
from urgap.uctl.run import run
from urgap.uctl.set import set_command
from urgap.uctl.show import show_credentials_click
from urgap.uctl.upload import upload

urgap.uinit.configure_logger()


@click.group()
def cli() -> None:
    """Start the urgap command-line interface (CLI)."""


# Register subcommands and command groups
cli.add_command(set_command, name="set")
cli.add_command(show_credentials_click, name="show")
cli.add_command(describe)
cli.add_command(run)
cli.add_command(info)
cli.add_command(upload)
