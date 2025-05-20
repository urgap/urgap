
"""

import click



@click.group()
def cli() -> None:

# Register subcommands and command groups
cli.add_command(describe)
cli.add_command(info)