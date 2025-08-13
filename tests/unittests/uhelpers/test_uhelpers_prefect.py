import json

import urgap

from urgap import URunDict
from urgap.uhelpers.prefect import (
    filter_by_uftype,
    parse_inputs,
    retrieve_processed_uris,
    run_unode,
    setup_urgap,
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
    },
]
CONFIG = {"i_hope": "this_gets_added"}


def test_parse_inputs(tmp_dir):
    p = tmp_dir / "default.json"
    with p.open("w") as file:
        json.dump({"pipeline_configuration": {"test": "value"}}, file)
    input_json = {"default_pipeline_config_json": p}
    urd, input_json = parse_inputs(input_json)
    assert "credentials_lookup" in input_json
    assert isinstance(urd, urgap.URunDict)


def test_setup_urgap():
    setup_urgap(ucredentials=CREDS, config=CONFIG)
    assert (
        "a_scheme://thats_a_host"
        in urgap.instances.ucredential_manager.ingested_credentials
    )
    assert "i_hope" in urgap.config


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
    uri = f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#unified_csvs/BSA1_xtandem_alanine_unified.csv"
    urd = urgap.URunDict(
        {
            "parameters": {"TestNode1:1.0.0": {}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    unode = "TestNode1:1.0.0"

    results = run_unode.fn(
        uris=uri,
        urd=urd,
        unode=unode,
        ucredentials=CREDS,
        config=CONFIG,
    )
    assert len(results) == 3
    for file in results:
        assert isinstance(file, str)


def test_simplify_output_names(tmp_dir):
    uris = [
        f"file://{urgap._test_folder}/data?parent_0=eJwrzctMy0xNiU8uLivWdwp2NIyvKEnMS0nNjU/MSczLzEuNL4Wo0AOqAACQjxF9#unified_csvs/BSA1_xtandem_alanine_unified.csv",
        f"file://{urgap._test_folder}/data?parent_0=eJwrzctMy0xNiU8uLivWT0nNzdcDsgBdDwhR#unified_csvs/demo.csv",
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
        f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#unified_csvs/BSA1_xtandem_alanine_unified.csv",
        f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#unified_csvs/demo.csv",
    ]
    filtered = filter_by_uftype.fn(uris=uris, uftype=[urgap.uftypes.test.TEST_FILE1])
    assert len(filtered) == 1

    filtered = filter_by_uftype.fn(
        uris=uris,
        uftype=[urgap.uftypes.test.TEST_FILE1, urgap.uftypes.test.TEST_FILE2],
    )
    assert len(filtered) == 2

    filtered = filter_by_uftype.fn(uris=uris, uftype=[urgap.uftypes.test.TEST_FILE3])
    assert len(filtered) == 0


def test_parse_inputs_no_default_file():
    input_json = {"pipeline_configuration": {"param": 42}}
    urd, updated_json = parse_inputs(input_json)

    assert isinstance(urd, URunDict)

    assert isinstance(updated_json, dict)

    assert updated_json["pipeline_configuration"]["param"] == 42


def test_parse_inputs_with_none_values():
    from urgap import URunDict

    input_json = {"pipeline_configuration": {"param1": None, "param2": 100}}

    urd, updated_json = parse_inputs(input_json)

    assert isinstance(urd, URunDict)

    pipeline_config = updated_json.get("pipeline_configuration", {})
    pipeline_args = []
    for key, value in pipeline_config.items():
        if value is None:
            pipeline_args.append(key)
        else:
            pipeline_args.append(f"{key}={value}")

    assert "param1" in pipeline_args
    assert "param2=100" in pipeline_args


def test_retrieve_processed_uris_empty_list(caplog):
    caplog.set_level("INFO")

    uris = []
    result = retrieve_processed_uris(uris)

    # Check that logger.info was called with the expected message
    assert "Nothing to receive here" in caplog.text
    # The result should still be an empty list
    assert result == []


def test_retrieve_processed_uris_with_none():
    uris = [None]
    result = retrieve_processed_uris(uris)
    assert result == [None]  # just check the output



    assert result is True