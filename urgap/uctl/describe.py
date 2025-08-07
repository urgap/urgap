"""Describe submodule of urgap.uctl."""

import logging
import pprint

import click

import urgap

logger = logging.getLogger(__name__)


@click.command()
@click.argument("wid")
def describe_wid_click(wid: str) -> None:
    """Retrieve UMeta information for a given WID (click wrapper).

    Note: Only works with mongo; requires umeta.UMeta.find_wid_members() to be implemented.
    """
    logger.info(pprint.pformat(describe_wid(wid)))


def describe_wid(wid: str) -> urgap.UReport | str:
    """Retrieve UMeta information for a given WID.

    Returns a UReport or a not-found message.
    """
    try:
        return urgap.UReport(wid=wid)
    except ValueError:
        return f"No History found for given wid: {wid}"


@click.command()
@click.argument("object_name")
def describe_object_name_click(object_name: str) -> None:
    """Retrieve UMeta information for a given object name (click wrapper)."""
    logger.info(pprint.pformat(describe_object_name(object_name)))


def describe_object_name(object_name: str) -> dict:
    """Retrieve UMeta information for a given object name.

    Returns a dictionary with producer and consumers.
    """
    um = urgap.UMeta()
    return {
    }


@click.command()



    Returns a UReport or a not-found message.
    """
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
    logger.info(pprint.pformat(describe_last_runs(unode, last=last)))


def describe_last_runs(unode: str, last: int = 10) -> list[tuple]:
    """Retrieve last n processed files for a given unode.

    Returns a list of (file, ...) tuples.
    """
    um = urgap.UMeta()
    return um.find_last_processed_files(unode, last=last)


@click.command()
@click.option("--storage_base_uri", "-s")
@click.option("--object_name", "-o")
@click.option("--ucfs", "-u")
def describe_ucfs_click(
    storage_base_uri: str | None = None,
    object_name: str | None = None,
    ucfs: str | None = None,
) -> None:
    """Retrieve UMeta information for a ucfs storage location with given options."""
    rows = describe_ucfs(
        storage_base_uri=storage_base_uri,
        object_name=object_name,
        ucfs=ucfs,
    )
    log_table(rows=rows)


def describe_ucfs(
    storage_base_uri: str | None = None,
    object_name: str | None = None,
    ucfs: str | None = None,
) -> urgap.UReport:
    """Retrieve UMeta information for ucfs storage location."""
    um = urgap.UMeta()
    return um.io.get_ucfs_object_name_info(
        storage_base_uri=storage_base_uri,
        object_name=object_name,
        ucfs=ucfs,
    )


def log_table(rows: list[dict] | None = None) -> None:
    """Format output as a table for UCFS storage location.

    Args:
        rows: List of UMeta entries.
    """
    if not rows:
        logger.info("No rows to display.")
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
    logger.info("\n%s", output)


@click.command()
def umeta() -> None:
    """Check metadata for UMeta."""


@click.command()
def unodes() -> None:
    """Check metadata for UNodes."""


@click.command()
def version() -> None:
    """Check metadata for URGAP version."""


@click.group()
def meta_info() -> None:
    """See specific resource metadata."""


meta_info.add_command(umeta)
meta_info.add_command(unodes)
meta_info.add_command(version)


@click.command()
def meta_creds() -> None:
    """See metadata for credentials."""


@click.group()
def describe() -> None:
    """Describe UMeta entries in more detail."""


describe.add_command(meta_info, name="info")
describe.add_command(meta_creds, name="credentials")
describe.add_command(describe_wid_click, name="wid")
describe.add_command(describe_object_name_click, name="object")
describe.add_command(describe_last_runs_click, name="history")
describe.add_command(describe_ucfs_click, name="ucfs")