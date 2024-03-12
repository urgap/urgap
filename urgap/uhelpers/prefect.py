
import json
import logging
from pathlib import Path
from time import sleep





    Args:

    Returns:
    """
    if default_config_json is not None:
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
        else:
            yield e



    Args:
    """


def retrieve_processed_uris(
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
    return uris


@task(retries=3, retry_delay_seconds=10)
def run_unode(
    unode: str,
    config: dict,
) -> list:

    Args:

    Returns:
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return [None]
    return [uf.as_uri() if uf is not None else None for uf in result]


@task(retries=10, retry_delay_seconds=10)
def simplify_output_names(
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
    if len(uris) == 0:
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

    Args:

    Returns:
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
        return None
    filtered_ufile_list = ufile_list.keep_uftypes(uftype)
    return [uf.as_uri() for uf in filtered_ufile_list]


@task(name="Rebase", retries=3, retry_delay_seconds=20)

    Args:
    """
    uris = retrieve_processed_uris(uris=uris)
    if None in uris:
    for uf in ufile_list:
        uf.rebase(uri=storage_base_uri, upload=True)


@flow(name="Import Flow")

    Args:
    """
    urd, input_json = parse_inputs(input_json=input_json)
    pipeline(urd, input_json)