from pathlib import Path

import urgap


def test_modifying_file_doesnt_change_ufile_list():
    tmp_string = "#unique"
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}&testtag=asdf#{tmp_string}/test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}&testtag=asdf#{tmp_string}/test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}&testtag=jkl#{tmp_string}/test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    index_groups = ufl.get_index_groups_by_tag(tag="testtag")

    assert len(index_groups) == 2
    assert index_groups["asdf"] == [0, 1]
    assert index_groups["jkl"] == [2]