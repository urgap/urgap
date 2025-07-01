
import json
import logging
import pprint
from typing import ParamSpec

P = ParamSpec("P")



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