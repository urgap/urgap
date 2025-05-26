import subprocess

import pytest



def test_utelemetry_run(provide_changeable_config):
        [
    )
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "`spectrum_id` > 3000",
            },
            "unode_parameters": {
            },
    )
    FilterTabularToCSV_node.run(urun_dict=urun_dict, ufiles=ufiles)


def test_utelemetry_run_remote_fails(provide_changeable_config, caplog):
        [
    )
        {
            "parameters": {
                "FilterTabularToCSV:1.0.0": {
                    "-q": "`spectrum_id` > 3000",
            },
            "unode_parameters": {
                "remote_url": "http://localhost",
            },
    )
    with pytest.raises(Exception):
        FilterTabularToCSV_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert (
        "Remote execution failed with error: HTTPConnectionPool(host='localhost'"
        in caplog.text
    )


def test_utelemetry_generates_output():
    result = subprocess.run(
        ["pytest", "-s", f"{__file__}::test_utelemetry_run"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert '"name": "ufiles-uploaded"' in result.stdout
    assert (
        '"name": "|       #0 Not all expected output file of type .any.csv exist."'
        in result.stdout
    )
    assert '"name": "| - run should be triggered, reasons:"' in result.stdout