"""Uctl module of urgap2.

This is the main CLI entrypoint and command group dispatcher for urgap2.
"""

import click

from urgap.uctl.info import info


@click.group()
def cli() -> None:
    """Start the urgap command-line interface (CLI)."""


# Register subcommands and command groups
cli.add_command(set_command, name="set")
cli.add_command(describe)
cli.add_command(info)
cli.add_command(upload)