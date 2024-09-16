
import collections
import click



@click.command()



    Args:
        condition: Availability of 3rd party/executable.

    Returns:
    """
    if condition is True:
        return click.style("[ yes ]", fg="bright_green")
        return click.style("[ no! ]", fg="red")


@click.command()
    placeholder_str = "|      "
    click.secho("Available Unodes", fg="bright_green")
    click.secho(
    )
    click.secho(
    )
    counter = collections.defaultdict(int)
    tags = set()
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
    for _ in range(0, len(sorted_tags), 7):


@click.command()
    for k, v in interface_stats.items():
        click.echo(f"{k: >50}:{v: >12}")