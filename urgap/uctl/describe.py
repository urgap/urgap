
import logging
import pprint
import click



@click.command()
@click.argument("wid")
def describe_wid_click(wid: str) -> None:
    """Retrieve UMeta information for a given WID (click wrapper).

    """


    try:
    except ValueError:
        return f"No History found for given wid: {wid}"


@click.command()
@click.argument("object_name")
def describe_object_name_click(object_name: str) -> None:


def describe_object_name(object_name: str) -> dict:
    return {
    }


@click.command()


    try:
    except ValueError:


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


@click.command()
@click.option("--storage_base_uri", "-s")
@click.option("--object_name", "-o")
def describe_ucfs_click(
    storage_base_uri: str | None = None,
    object_name: str | None = None,
) -> None:
    rows = describe_ucfs(
    )
    log_table(rows=rows)


def describe_ucfs(
    storage_base_uri: str | None = None,
    object_name: str | None = None,
    """Retrieve UMeta information for ucfs storage location."""
    return um.io.get_ucfs_object_name_info(
    )


def log_table(rows: list[dict] | None = None) -> None:

    Args:
        rows: List of UMeta entries.
    """
    if not rows:
        return
    # Extract column headers from the first row
    headers = rows[0].keys()
    # Calculate column widths
    col_widths = {
        key: max([len(str(key))] + [len(str(row[key])) for row in rows])
        for key in headers
    }
    # Format header
    header_row = " | ".join(f"{key.upper():<{col_widths[key]}}" for key in headers)
    divider = "-+-".join("-" * col_widths[key] for key in headers)
    # Format rows
    row_lines = [
        " | ".join(f"{row[key]!s:<{col_widths[key]}}" for key in headers)
        for row in rows
    ]
    # Combine and log
    output = "\n".join([header_row, divider, *row_lines])