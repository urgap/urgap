"""Info submodule of urgap.uctl."""

import collections
import logging
import pprint

import click

import urgap


@click.command()
def info_version_click() -> None:
    """Show the version number of the installed Urgap package."""


def get_status(condition: bool | None) -> click.style:
    """Return colored status for 3rd party/executable availability.

    Args:
        condition: Availability of 3rd party/executable.

    Returns:
        Colorized click.style based on availability.
    """
    if condition is True:
        return click.style("[ yes ]", fg="bright_green")
    if condition is False:
        return click.style("[ no! ]", fg="red")
    return click.style("[ ... ]", fg="white")


@click.command()
def info_unodes_click() -> None:
    """Show availability and status of all unodes."""
    placeholder_str = "|      "
    click.secho("Available Unodes", fg="bright_green")
    click.secho("{: >45}".format("name"))
    click.secho("{: >45} {}".format("    ", "Executable available"))
    click.secho(
        "{: >45} {} {}".format(
            "    ",
            placeholder_str,
            "3rd party installations required / available",
        ),
    )
    click.secho(
        "{: >45} {} {} {}".format(
            "    ",
            placeholder_str,
            "Wrapper version",
            "Engine type",
        ),
    )
    click.secho(
        "{: >45} {} {} {}".format(
            "    ",
            placeholder_str,
            placeholder_str,
            placeholder_str,
        ),
    )
    counter = collections.defaultdict(int)
    tags = set()
    for k in sorted(urgap.instances.unode_manager.wrapper_lookup.keys()):
        if "TestNode" in k:
            counter["test_nodes"] += 1
            continue
        counter["unodes"] += 1
        v = urgap.init_node(k)
        if v.requires_3rd_party_installation is True:
            status_3rd_party = get_status(v.has_all_required_installations())
        else:
            status_3rd_party = get_status(None)
        exe_available = get_status(v.is_available)
        w = v.META_INFO.get(
            "wrapper_version",
            {"major": "x", "minor": "x", "patch": "x"},
        )
        wrapper_version = "{major}.{minor}.{patch}".format(**w)
        is_of_engine_type = ", ".join(v.META_INFO["engine_type"])
        tags |= set(v.META_INFO["engine_type"])
        click.echo(
            f"{k: >45} {exe_available} {status_3rd_party} {wrapper_version: >7s} : {is_of_engine_type}",
        )
    click.echo(
        "\nIn summary a total {unodes} wrappers are available. Not showing {test_nodes} test_nodes".format(
            **counter,
        ),
    )
    click.echo(f"Total number of tags {len(tags)}")
    sorted_tags = sorted(tags)
    for _ in range(0, len(sorted_tags), 7):
        click.echo(f"       {', '.join(sorted_tags[_ : _ + 7])}")


@click.command()
def info_umeta_click() -> None:
    """Show UMeta interface statistics."""
    interface_stats = urgap.UMeta().retrieve_interface_statistics()
    click.secho(f"UMeta {urgap.config['umeta']}", fg="bright_green")
    for k, v in interface_stats.items():
        click.echo(f"{k: >50}:{v: >12}")


@click.group()
def info() -> None:
    """Show information about the Urgap installation."""


info.add_command(info_version_click, name="version")
info.add_command(info_umeta_click, name="umeta")
info.add_command(info_unodes_click, name="unodes")