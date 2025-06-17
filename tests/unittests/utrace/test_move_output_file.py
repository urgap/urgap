import tempfile



        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
    assert ut.output_files[0].path.exists()
    assert len(ut.output_files) == 1


        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
        )
    assert ut.output_files[0].path.exists()
    assert len(ut.output_files) == 1


        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    assert len(ut.output_files) == 2
    assert ut.output_files[0].path.exists()
    assert ut.output_files[1].path.exists()


        [
            ),
    )
        urun_dict=urd,
        input_files=input_files,
    )
    assert ut.output_files[1].path.exists()
    assert len(ut.output_files) == 2