from click.testing import CliRunner

runner = CliRunner()


def test_upload_folder_click(tmp_dir, caplog):
    result = runner.invoke(
        upload_folder_click,
        [
            f"file://{tmp_dir}",
            "test",
        ],
    )
    assert "Upload finished, final uris:" in caplog.text
    expected_tqdm_output = [
        "Uploading:",
        "Processing file human_ecoli_sample_pyiohat.csv:",
        "Processing file BSA1_xtandem_alanine_unified.csv:",
        "Processing file demo.csv:",
    ]
    for expected in expected_tqdm_output: