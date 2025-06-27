import tempfile



def test_move_output_file(tmp_scratch_disk):
        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
        ut.move_output_files(
            files=[tmp_file.name],
        )
    assert ut.output_files[0].path.exists()
    assert len(ut.output_files) == 1


def test_move_output_file_keep_original_name(tmp_scratch_disk):
        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
        ut.move_output_files(
            files=[tmp_file.name],
            keep_original_name=True,
        )
    assert ut.output_files[0].path.exists()
    assert len(ut.output_files) == 1
    assert ut.output_files[0].tags["original_name"] == tmp_file.name


def test_move_output_file_twice(tmp_scratch_disk):
        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    files = [
        tempfile.NamedTemporaryFile(delete=False).name,
        tempfile.NamedTemporaryFile(delete=False).name,
    ]
    ut.move_output_files(
        files=files,
        extend_len=1,
    )
    assert len(ut.output_files) == 2
    assert ut.output_files[0].path.exists()
    assert ut.output_files[1].path.exists()


def test_move_output_file_twice_with_original_name(tmp_scratch_disk):
        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    files = [
        tempfile.NamedTemporaryFile(delete=False).name,
        tempfile.NamedTemporaryFile(delete=False).name,
    ]
    ut.move_output_files(
        files=files,
        extend_len=1,
        keep_original_name=True,
    )
    assert ut.output_files[0].path.exists()
    assert ut.output_files[1].path.exists()
    assert len(ut.output_files) == 2
    assert ut.output_files[0].tags["original_name"] == files[0]
    assert ut.output_files[1].tags["original_name"] == files[1]