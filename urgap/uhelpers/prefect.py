
import json
import logging

from collections.abc import Generator, Iterable
from pathlib import Path
from time import sleep
from typing import ParamSpec

from prefect import flow, task


P = ParamSpec("P")
INCOMPLETE_WARNING = "Incomplete inputs. Skipping task."



    Args:

    Returns:
    """
    default_config_json = input_json.get("default_pipeline_config_json")
    if default_config_json is not None:
        default_config_json = Path(default_config_json).resolve()
            default_pipeline_args = json.load(jf)
    else:
        default_pipeline_args = {}

    if "credentials_lookup" not in input_json:
        input_json["credentials_lookup"] = None

    # Extract pipeline configuration from default configuration
    pipeline_config = default_pipeline_args.get("pipeline_configuration", {})
    # Overwrite with explicit pipeline configuration
    pipeline_config.update(input_json.get("pipeline_configuration", {}))

    pipeline_args = []
    for key, value in pipeline_config.items():
        if value is None:
            pipeline_args.append(key)
        else:
            pipeline_args.append(f"{key}={value}")

    return urd, input_json


def flatten_no_strings(iterable: Iterable) -> Generator:

    Args:

    Returns:
    """
    for e in iterable:
        if hasattr(e, "__iter__") and not isinstance(e, str):
            yield from flatten_no_strings(e)
        else:
            yield e



    Args:
    """


def retrieve_processed_uris(
    uris: list[str] | str,
) -> list:

    Args:

    Returns:
    """
    if isinstance(uris, str) or (uris is None):
        uris = [uris]
    else:
        uris = list(flatten_no_strings(uris))
    if len(uris) == 0:
    elif not (isinstance(uris[0], str) or (uris[0] is None)):
        while True:
            uris = [uri.get_state() for uri in uris]
            if (len(set(uris)) == 1) and ("plete" in uris[0].lower()):
                break
            sleep(5)
    return uris


@task(retries=3, retry_delay_seconds=10)
def run_unode(
    uris: list[str] | str,
    unode: str,
    ucredentials: list[dict],
    config: dict,
    **kwargs: P.kwargs,
) -> list:

    Args:

    Returns:
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return [None]
    result = node.run(ufiles=uris, urun_dict=urd, **kwargs)
    return [uf.as_uri() if uf is not None else None for uf in result]


@task(retries=10, retry_delay_seconds=10)
def simplify_output_names(
    uris: list[str] | str,
    ucredentials: dict,
    config: dict,
    sources: list,
    prefix: str,
    suffix: str,
    storage_base_uri: str,
) -> None:

    Args:

    Returns:
        None.
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return
    if len(uris) == 0:
        return
    source_uris = retrieve_processed_uris(uris=sources)
    source_object_names = set()
    for uri in source_uris:
        source_object_names.add(uri.split("#")[-1])
    ufiles.simplify_names(
        source_object_names=source_object_names,
        prefix=prefix,
        suffix=suffix,
        storage_base_uri=storage_base_uri,
    )


@task(name="Filter uftypes", retries=3, retry_delay_seconds=10)
def filter_by_uftype(
    uris: list[str] | str,
    uftype: list,
) -> list | None:

    Args:

    Returns:
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return None
    filtered_ufile_list = ufile_list.keep_uftypes(uftype)
    return [uf.as_uri() for uf in filtered_ufile_list]


@task(name="Group by tag", retries=3, retry_delay_seconds=10)
def group_by_tag(
    uris: list[str] | str,
    tag: str,
) -> dict | None:

    Args:

    Returns:
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return None
    index_groups = ufile_list.get_index_groups_by_tag(tag=tag)
    return {k: [ufile_list[idx].as_uri() for idx in v] for k, v in index_groups.items()}


@task(name="Rebase", retries=3, retry_delay_seconds=20)
def rebase(

    Args:
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
    for uf in ufile_list:
        uf.rebase(uri=storage_base_uri, upload=True)


@flow(name="Import Flow")
def import_flow(flow_str: str, flow_name: str, input_json: dict) -> None:

    Args:
    """
    if pipeline is None:
        raise ValueError(msg)
    urd, input_json = parse_inputs(input_json=input_json)
    pipeline(urd, input_json)