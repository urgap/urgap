from click.testing import CliRunner

import urgap

from urgap.uctl.upload import upload_folder_click

runner = CliRunner()


def test_upload_folder_click(tmp_dir, caplog):
    result = runner.invoke(
        upload_folder_click,
        [
            f"{urgap._test_folder}/data/unified_csvs",
            f"file://{tmp_dir}",
            "test",
        ],
    )
    assert "Upload finished, final uris:" in caplog.text
    assert "16c0cea811a829ae630bb6559508e82c" in caplog.text
    expected_tqdm_output = [
        "Uploading:",
        "Processing file human_ecoli_sample_pyiohat.csv:",
        "Processing file BSA1_xtandem_alanine_unified.csv:",
        "Processing file demo.csv:",
    ]
    for expected in expected_tqdm_output:
        assert expected in (result.stdout + result.stderr)
