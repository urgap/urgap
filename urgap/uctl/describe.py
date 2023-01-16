
import click



@click.command()
@click.argument("wid")
    """Retrieve UMeta information for a given WID (click wrapper).

    """




@click.command()
@click.argument("object_name")


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
    """Retrieve last n processed files for a given unode (click wrapper)."""


    return um.find_last_processed_files(unode, last=last)