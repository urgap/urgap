
import click



@click.group()
def cli() -> None:

cli.add_command(describe)
cli.add_command(info)