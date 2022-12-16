
import click



@click.command()
@click.argument("wid")
    """Retrieve UMeta information for a given WID (click wrapper).

    """




@click.command()
@click.argument("object_name")





@click.command()
@click.option(
    "--last",
    "-l",
    "last",
    help="Show the last n ufiles created by the node",
    default=10,
)

