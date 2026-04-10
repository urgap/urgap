import subprocess

import pytest

import urgap


def test_utelemetry_run(provide_changeable_config):
    urgap.config["opentelemetry_exporter_type"] = "Console"
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV}"
                f"#unified_csvs/demo.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "`spectrum_id` > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{urgap.scratch_disk}",
            },
        },
    )
    FilterTabularToCSV_node = urgap.init_unode("FilterTabularToCSV:1.0.0")
    FilterTabularToCSV_node.run(urun_dict=urun_dict, ufiles=ufiles)
    urgap.utl.shutdown()


def test_utelemetry_run_remote_fails(provide_changeable_config, caplog):
    urgap.config["opentelemetry_exporter_type"] = "Console"
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.proteomics.validator.PEPTIDEFOREST_CSV}"
                f"#unified_csvs/demo.csv",
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "`spectrum_id` > 3000",
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{urgap.scratch_disk}",
                "remote_url": "http://localhost",
            },
        },
    )
    FilterTabularToCSV_node = urgap.init_unode("FilterTabularToCSV:1.0.0")
    with pytest.raises(Exception):
        FilterTabularToCSV_node.run(urun_dict=urun_dict, ufiles=ufiles)


def test_utelemetry_generates_output():
    result = subprocess.run(
        ["pytest", "-s", f"{__file__}::test_utelemetry_run"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert '"name": "ufiles-uploaded"' in result.stdout
    assert '"name": "urgap_node_execution"' in result.stdout
    assert '"pac_id": "FilterTabularToCSV_1.0.0_' in result.stdout
    assert (
        '"name": "|       #0 Not all expected output file of type .any.csv exist."'
        in result.stdout
    )
    assert '"name": "| - run should be triggered, reasons:"' in result.stdout
