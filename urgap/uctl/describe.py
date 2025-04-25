
import logging
import pprint
import click



@click.command()
@click.argument("wid")
def describe_wid_click(wid: str) -> None:
    """Retrieve UMeta information for a given WID (click wrapper).

    """




@click.command()
@click.argument("object_name")
def describe_object_name_click(object_name: str) -> None:


def describe_object_name(object_name: str) -> dict:
    return {
    }


@click.command()




@click.command()
@click.argument("unode")
@click.option(
    "--last",
    "-l",
    "last",
    help="Show the last n ufiles created by the node",
    default=10,
)
def describe_last_runs_click(unode: str, last: int = 10) -> None:
    """Retrieve last n processed files for a given unode (click wrapper)."""


def describe_last_runs(unode: str, last: int = 10) -> list[tuple]:
    return um.find_last_processed_files(unode, last=last)