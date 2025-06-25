

def test_upload_ufiles(tmp_scratch_disk, caplog) -> None:
    for uf in ufl:
        uf.rebase(f"file://{tmp_scratch_disk}")
    ufl.upload_ufiles()
    assert "Starting upload of UFileList in parallel with 1 threads." in caplog.text


def test_upload_ufiles_8_threads(tmp_scratch_disk, caplog) -> None:
    for uf in ufl:
        uf.rebase(f"file://{tmp_scratch_disk}")
    ufl.upload_ufiles(number_of_threads=8)
    assert "Starting upload of UFileList in parallel with 8 threads." in caplog.text


def test_upload_ufiles_from_config(tmp_scratch_disk, caplog) -> None:
    for uf in ufl:
        uf.rebase(f"file://{tmp_scratch_disk}")
    ufl.upload_ufiles()
    assert "Starting upload of UFileList in parallel with 10 threads." in caplog.text