import json


    filter_by_uftype,
    parse_inputs,
    retrieve_processed_uris,
    run_unode,
    simplify_output_names,
)

CREDS = [
    {
        "host": "thats_a_host",
        "user": "a_user",
        "scheme": "a_scheme",
        "secure": True,
        "password": "very_safe",
        "description": "what a cred",
        "secret_store": "env",
]
CONFIG = {"i_hope": "this_gets_added"}


def test_parse_inputs(tmp_dir):
    p = tmp_dir / "default.json"
    with p.open("w") as file:
        json.dump({"pipeline_configuration": {"test": "value"}}, file)
    input_json = {"default_pipeline_config_json": p}
    urd, input_json = parse_inputs(input_json)
    assert "credentials_lookup" in input_json


    assert (
        "a_scheme://thats_a_host"
    )


def test_retrieve_processed_uris():
    uri = "file:///only/one#string.txt"
    single = retrieve_processed_uris(uri)
    assert len(single) == 1
    assert isinstance(single[0], str)

    more_uris = ["file:///second/urgap#string.txt", "file:///thirds/the#charm.txt"]
    single.append(more_uris)
    assert len(single) == 2
    flattened = retrieve_processed_uris(single)
    assert len(flattened) == 3


def test_run_unode(tmp_dir):
        {
            "parameters": {"TestNode1:1.0.0": {}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    unode = "TestNode1:1.0.0"

    results = run_unode.fn(
    )
    assert len(results) == 3
    for file in results:
        assert isinstance(file, str)


def test_simplify_output_names(tmp_dir):
    uris = [
    ]
    simplify_output_names.fn(
        uris=[None],
        ucredentials=CREDS,
        config=CONFIG,
        sources=uris,
        prefix="pre",
        suffix="suff",
        storage_base_uri=f"file://{tmp_dir}",
    )
    assert len(list(tmp_dir.iterdir())) == 0

    simplify_output_names.fn(
        uris=uris,
        ucredentials=CREDS,
        config=CONFIG,
        sources=uris,
        prefix="pre_",
        suffix="suff.txt",
        storage_base_uri=f"file://{tmp_dir}",
    )
    copied_files = list(tmp_dir.iterdir())
    assert len(copied_files) == 2
    for filename in copied_files:
        assert filename.name in (
            "pre_demosuff.txt",
            "pre_BSA1_xtandem_alanine_unifiedsuff.txt",
        )


def test_filter_by_uftype():
    uris = [
    ]
    assert len(filtered) == 1

    filtered = filter_by_uftype.fn(
        uris=uris,
    )
    assert len(filtered) == 2

    assert len(filtered) == 0