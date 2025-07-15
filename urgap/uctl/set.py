"""Set submodule of urgap.uctl."""

import json
import logging
import pprint
from typing import ParamSpec

P = ParamSpec("P")

URGAP_HOME_JSON = urgap.home / "urgap.json"


def _check_if_config_key_value_is_valid(
    config: dict,
    config_key: str,
    config_value: str,
    verbose: bool = False,
) -> bool:
    """Check if a config key/value pair is valid."""
    if verbose is True:
    is_valid = True
    if config_key not in config:
        msg = f"{config_key} is not in urgap.json, thus cannot be set ..."
        is_valid = False
    else:
        options = config[config_key].get("options", None)
        if (options is not None) and (config_value not in options):
            msg = f"{config_key} cannot be set with {config_value}. Valid options are {options}."
            is_valid = False
    return is_valid


def set_config(
    config_key: str,
    config_value: str,
    verbose: bool = False,
    **kwargs: P.kwargs,
) -> None:
    """Set urgap config key/value pairs in $URGAP_HOME/urgap.json."""
    if config_value in ("true", "false", "null"):
        config_value = json.loads(config_value)
    with URGAP_HOME_JSON.open() as config_json:
        config = json.load(config_json)
    kv_is_valid = _check_if_config_key_value_is_valid(
        config,
        config_key,
        config_value,
        verbose=verbose,
    )
    if kv_is_valid:
        if isinstance(config[config_key]["value"], list):
            config_value = [x.strip() for x in config_value.split(",")]
        config[config_key]["value"] = config_value

        if kwargs.get("dry", False) is True and verbose is True:
            msg = (
                f"Dry-run. Modified urgap.json entry for {config_key} would look like:"
            )
        else:
            with URGAP_HOME_JSON.open("w") as config_json:
                json.dump(config, config_json, indent=4, sort_keys=True)
            if verbose is True:
                msg = f"Modifying urgap.json entry for {config_key} to:"


@click.command()
@click.argument("config_key")
@click.argument("config_value")
@click.option(
    "--dry",
    "-d",
    "dry",
    is_flag=True,
    help="Boolean flag whether to update config",
)
def set_config_click(config_key: str, config_value: str, **kwargs: P.kwargs) -> None:
    """Set urgap config key/value pairs (Click wrapper).

    If the original value is a list, the value type will be maintained.
    Use ',' to separate entries in the list.
    """
    set_config(config_key, config_value, **kwargs, verbose=True)


def set_credentials(cred_key: str, **kwargs: P.kwargs) -> None:
    """Set credentials metadata in $URGAP_HOME/credentials_lookup.json.

    Updates the entry for the given cred_key with provided options.
    Use --dry for a dry-run (no file changes).
    """
    cred_entry = urgap.instances.ucredential_manager.ingested_credentials.get(
        cred_key,
        None,
    )

    if cred_entry is not None:
        dry_run = kwargs.get("dry")
        del kwargs["dry"]
        for k, v in kwargs.items():
            if v is None:
                continue
            if k == "secure":
                urgap.instances.ucredential_manager.ingested_credentials[cred_key][
                    k
                ] = v != "False"
            else:
                urgap.instances.ucredential_manager.ingested_credentials[cred_key][
                    k
                ] = v
        if dry_run:
        else:
            msg = f"Changed entry for {cred_key} to:"
            urgap.instances.ucredential_manager.write_credentials()
        _log_cred_entry(cred_entry)


def _log_cred_entry(cred_entry: dict) -> None:
    """Log all key-value pairs in the credential entry."""
    for k, v in cred_entry.items():
        msg = f"{k: >20}:{v}"


@click.command()
@click.argument("cred_key")
@click.option("--scheme", "-s", "scheme", default=None, help="Set scheme")
@click.option("--host", "-h", "host", default=None, help="Set host")
@click.option("--user", "-u", "user", default=None, help="Set user id")
@click.option("--password", "-p", "password", default=None, help="Set password id")
@click.option(
    "--store",
    "secret_store",
    default=None,
    help="Set secret store backend",
)
@click.option("--secure", "-x", "secure", default=None, help="Use secure channels")
@click.option(
    "--dry",
    "-d",
    "dry",
    is_flag=True,
    help="Boolean flag whether to update json",
)
def set_credentials_click(cred_key: str, **kwargs: P.kwargs) -> None:
    """Set credentials metadata in $URGAP_HOME/credentials_lookup.json (Click wrapper)."""
    set_credentials(cred_key, **kwargs)


@click.group()
def set_command() -> None:
    """Set specific features on objects."""


set_command.add_command(set_config_click, name="config")
set_command.add_command(set_credentials_click, name="credentials")