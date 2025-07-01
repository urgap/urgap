import tempfile

import urgap


def test_move_output_file(tmp_scratch_disk):
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?output_file_index="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
            ),
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode1:1.0.0").META_INFO,
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
        ut.move_output_files(
            files=[tmp_file.name],
            uftype=urgap.uftypes.test.TEST_FILE2,
        )
    assert ut.output_files[0].path.exists()
    assert len(ut.output_files) == 1


def test_move_output_file_keep_original_name(tmp_scratch_disk):
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?output_file_index="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
            ),
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode1:1.0.0").META_INFO,
    )
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
        ut.move_output_files(
            files=[tmp_file.name],
            uftype=urgap.uftypes.test.TEST_FILE2,
            keep_original_name=True,
        )
    assert ut.output_files[0].path.exists()
    assert len(ut.output_files) == 1
    assert ut.output_files[0].tags["original_name"] == tmp_file.name


def test_move_output_file_twice(tmp_scratch_disk):
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?output_file_index="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
            ),
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode1:1.0.0").META_INFO,
    )
    files = [
        tempfile.NamedTemporaryFile(delete=False).name,
        tempfile.NamedTemporaryFile(delete=False).name,
    ]
    ut.move_output_files(
        files=files,
        uftype=urgap.uftypes.test.TEST_FILE2,
        extend_len=1,
    )
    assert len(ut.output_files) == 2
    assert ut.output_files[0].path.exists()
    assert ut.output_files[1].path.exists()


def test_move_output_file_twice_with_original_name(tmp_scratch_disk):
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?output_file_index="
                f"{urgap.uftypes.test.TEST_FILE1}#csvs"
            ),
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode1:1.0.0").META_INFO,
    )
    files = [
        tempfile.NamedTemporaryFile(delete=False).name,
        tempfile.NamedTemporaryFile(delete=False).name,
    ]
    ut.move_output_files(
        files=files,
        uftype=urgap.uftypes.test.TEST_FILE2,
        extend_len=1,
        keep_original_name=True,
    )
    assert ut.output_files[0].path.exists()
    assert ut.output_files[1].path.exists()
    assert len(ut.output_files) == 2
    assert ut.output_files[0].tags["original_name"] == files[0]
    assert ut.output_files[1].tags["original_name"] == files[1]