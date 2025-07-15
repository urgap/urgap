"""Show submodule of urgap.uctl."""

import json
import logging
import pprint

import click

import urgap

from urgap.uctl.info import info

URGAP_HOME_JSON = urgap.home / "urgap.json"


@click.command()
@click.argument("cred_key")
def show_credentials_click(cred_key: str) -> None:
    """Show credentials for a given cred_key. Format: {scheme}://{host}."""
    show_credentials(cred_key)


def _log_cred_entry(cred_entry: dict) -> None:
    """Log all key-value pairs in the credential entry."""
    for k, v in cred_entry.items():
        msg = f"{k: >20}:{v}"


def show_credentials(cred_key: str) -> None:
    """Show credentials for a given cred_key.

    Displays all fields for the entry in {scheme}://{host} format.
    """
    cred_entry = urgap.instances.ucredential_manager.ingested_credentials.get(
        cred_key,
        None,
    )
    if cred_entry is not None:
        _log_cred_entry(cred_entry)
    else:


@click.command()
@click.option("--output", "-o", help="Output format")
def show_config_click(output: str) -> None:
    """Show current config (Click wrapper)."""
    show_config(output)


def show_config(output: str) -> None:
    """Display current configuration."""
    if output not in ["json"]:
        output = "pprint"
    with URGAP_HOME_JSON.open() as config_json:
        config = json.load(config_json)
    if output == "pprint":
    if output == "json":
    else:


@click.group()
def show() -> None:
    """Show values in urgap."""


show.add_command(show_config_click, name="config")
show.add_command(show_credentials_click, name="credentials")
show.add_command(info)