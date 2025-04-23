
import collections
import click



@click.command()
def info_version_click() -> None:


def get_status(condition: bool | None) -> click.style:

    Args:
        condition: Availability of 3rd party/executable.

    Returns:
    """
    if condition is True:
        return click.style("[ yes ]", fg="bright_green")
    if condition is False:
        return click.style("[ no! ]", fg="red")
    return click.style("[ ... ]", fg="white")


@click.command()
def info_unodes_click() -> None:
    placeholder_str = "|      "
    click.secho("Available Unodes", fg="bright_green")
    click.secho("{: >45}".format("name"))
    click.secho("{: >45} {}".format("    ", "Executable available"))
    click.secho(
        "{: >45} {} {}".format(
    )
    click.secho(
        "{: >45} {} {} {}".format(
    )
    click.secho(
        "{: >45} {} {} {}".format(
    )
    counter = collections.defaultdict(int)
    tags = set()
        if "TestNode" in k:
            counter["test_nodes"] += 1
            continue
        counter["unodes"] += 1
        if v.requires_3rd_party_installation is True:
            status_3rd_party = get_status(v.has_all_required_installations())
        else:
            status_3rd_party = get_status(None)
        exe_available = get_status(v.is_available)
        w = v.META_INFO.get(
        )
        wrapper_version = "{major}.{minor}.{patch}".format(**w)
        is_of_engine_type = ", ".join(v.META_INFO["engine_type"])
        tags |= set(v.META_INFO["engine_type"])
        click.echo(
        )
    click.echo(
        "\nIn summary a total {unodes} wrappers are available. Not showing {test_nodes} test_nodes".format(
    )
    click.echo(f"Total number of tags {len(tags)}")
    sorted_tags = sorted(tags)
    for _ in range(0, len(sorted_tags), 7):
        click.echo(f"       {', '.join(sorted_tags[_ : _ + 7])}")


@click.command()
def info_umeta_click() -> None:
    for k, v in interface_stats.items():
        click.echo(f"{k: >50}:{v: >12}")