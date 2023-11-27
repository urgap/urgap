import json
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



    Args:

    Returns:
    """
    for e in iterable:
        if hasattr(e, "__iter__") and not isinstance(e, str):
        else:
            yield e



    Args:
    """



    Args:

    Returns:
    """
        uris = [uris]
    else:
        uris = list(flatten_no_strings(uris))
        while True:
            uris = [uri.get_state() for uri in uris]
            if (len(set(uris)) == 1) and ("plete" in uris[0].lower()):
                break
    return uris


@task(retries=3, retry_delay_seconds=10)

    Args:

    Returns:
    """
    uris = retrieve_processed_uris(uris=uris)


@task(retries=10, retry_delay_seconds=10)
def simplify_output_names(

    Args:
    """
    uris = retrieve_processed_uris(uris=uris)
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

    Args:

    Returns:
    """
    filtered_ufile_list = ufile_list.keep_uftypes(uftype)
    return [uf.as_uri() for uf in filtered_ufile_list]


@flow(name="Import Flow")

    Args:
    """
    urd, input_json = parse_inputs(input_json=input_json)
    pipeline(urd, input_json)