
import json
import logging
import pprint



def _check_if_config_key_value_is_valid(
    config: dict,
    config_key: str,
    config_value: str,
    verbose: bool = False,
) -> bool:
    if verbose is True:
    is_valid = True
    if config_key not in config:
        is_valid = False
    else:
        options = config[config_key].get("options", None)
        if (options is not None) and (config_value not in options):
            is_valid = False
    return is_valid


def set_config(
    config_key: str,
    config_value: str,
    verbose: bool = False,
) -> None:
    if config_value in ("true", "false", "null"):
        config_value = json.loads(config_value)
        config = json.load(config_json)
    kv_is_valid = _check_if_config_key_value_is_valid(
        config,
        config_key,
        config_value,
        verbose=verbose,
    )
        if isinstance(config[config_key]["value"], list):
            config_value = [x.strip() for x in config_value.split(",")]
        config[config_key]["value"] = config_value

                json.dump(config, config_json, indent=4, sort_keys=True)