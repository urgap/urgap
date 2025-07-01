"""UHelpers for prefect of urgap2."""

import json
import logging
import tempfile

from collections.abc import Generator, Iterable
from pathlib import Path
from time import sleep
from typing import ParamSpec

from prefect import flow, task
from prefect.flows import load_flow_from_entrypoint

import urgap

P = ParamSpec("P")
INCOMPLETE_WARNING = "Incomplete inputs. Skipping task."


def parse_inputs(input_json: dict) -> tuple[urgap.URunDict, dict]:
    """Parse input config for Prefect-based urgap pipeline.

    Args:
        input_json: Configuration as Python dict.

    Returns:
        Tuple of URunDict and updated input_json.
    """
    default_config_json = input_json.get("default_pipeline_config_json")
    if default_config_json is not None:
        default_config_json = Path(default_config_json).resolve()
        with default_config_json.open() as jf:
            default_pipeline_args = json.load(jf)
    else:
        default_pipeline_args = {}

    if "credentials_lookup" not in input_json:
        input_json["credentials_lookup"] = None
    urd = urgap.URunDict(input_json.get("urun_dict", {}))

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
    """Flatten a nested iterable, but do not treat strings as iterables.

    Args:
        iterable: Nested iterable (may contain strings).

    Returns:
        Generator yielding flattened items.
    """
    for e in iterable:
        if hasattr(e, "__iter__") and not isinstance(e, str):
            yield from flatten_no_strings(e)
        else:
            yield e


def setup_urgap(ucredentials: list[dict], config: dict) -> None:
    """Initialize urgap config and credentials.

    Args:
        ucredentials: List of credentials dicts.
        config: urgap configuration dict.
    """
    urgap.config.update(config)
    urgap.instances.ucredential_manager.add_credentials(ucredentials)


def retrieve_processed_uris(
    uris: list[str] | str,
) -> list:
    """Resolve/flatten UUris for further processing.

    Args:
        uris: List of UUri strings or a single UUri string.

    Returns:
        List of resolved UUri strings.
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
    urd: urgap.URunDict,
    unode: str,
    ucredentials: list[dict],
    config: dict,
    **kwargs: P.kwargs,
) -> list:
    """Run a UNode as a Prefect task.

    Args:
        uris: Input UUris (list or single string).
        urd: URunDict configuration.
        unode: UNode name.
        ucredentials: List of credential dicts.
        config: urgap config dict.
        kwargs: Passed through to UNode.run.

    Returns:
        List of output UUris, or [None] if incomplete.
    """
    setup_urgap(ucredentials=ucredentials, config=config)
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return [None]
    node = urgap.init_node(unode)
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
    """Copy and rename UFiles to user-friendly output names.

    Args:
        uris: Input UUris (list or single string).
        ucredentials: Credentials dict.
        config: urgap config dict.
        sources: List of source file UUris.
        prefix: Prefix for new file names.
        suffix: Suffix for new file names.
        storage_base_uri: If set, output files will be rebased to this storage.

    Returns:
        None.
    """
    setup_urgap(ucredentials=ucredentials, config=config)
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return
    if len(uris) == 0:
        return
    ufiles = urgap.UFileList().from_uri_list(uri_list=uris)
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
    """Filter a UFileList to keep only specified uftypes.

    Args:
        uris: Input UUris (list or single string).
        uftype: List of uftypes to keep.

    Returns:
        List of filtered UUris, or None if incomplete input.
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return None
    ufile_list = urgap.UFileList().from_uri_list(uri_list=uris)
    filtered_ufile_list = ufile_list.keep_uftypes(uftype)
    return [uf.as_uri() for uf in filtered_ufile_list]


@task(name="Group by tag", retries=3, retry_delay_seconds=10)
def group_by_tag(
    uris: list[str] | str,
    tag: str,
) -> dict | None:
    """Group UFileList by a tag.

    Args:
        uris: Input UUris (list or single string).
        tag: Tag to group by.

    Returns:
        Dict of tag values to lists of UUris, or None if incomplete input.
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return None
    ufile_list = urgap.UFileList().from_uri_list(uri_list=uris)
    index_groups = ufile_list.get_index_groups_by_tag(tag=tag)
    return {k: [ufile_list[idx].as_uri() for idx in v] for k, v in index_groups.items()}


@task(name="Rebase", retries=3, retry_delay_seconds=20)
def rebase(
    uris: list,
    storage_base_uri: str,
    ucredentials: list[dict],
    config: dict,
) -> bool:
    """Rebase UFiles to a new storage base UUri.

    Args:
        uris: List of UUris.
        storage_base_uri: New storage base UUri.
        ucredentials: List of credentials.
        config: urgap config dict.

    Returns:
        bool: True on success otherwise False.
    """
    setup_urgap(ucredentials=ucredentials, config=config)
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return False
    ufile_list = urgap.UFileList().from_uri_list(uri_list=uris)
    for uf in ufile_list:
        uf.rebase(uri=storage_base_uri, upload=True)
    return True


@flow(name="Import Flow")
def import_flow(flow_str: str, flow_name: str, input_json: dict) -> None:
    """Import and run a Prefect flow from source string.

    Args:
        flow_str: Python source code for the flow.
        flow_name: Name of the flow in the source code.
        input_json: urgap input_json for the run.
    """
    pipeline = None

    with tempfile.NamedTemporaryFile(
        mode="wt",
        suffix=".py",
    ) as tmpfile:
        tmpfile.write(flow_str)
        tmpfile.flush()
        pipeline = load_flow_from_entrypoint(f"{tmpfile.name}:{flow_name}")
    if pipeline is None:
        msg = f"flow '{flow_name}' not found in flow scripts."
        raise ValueError(msg)
    urd, input_json = parse_inputs(input_json=input_json)
    pipeline(urd, input_json)