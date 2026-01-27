from pathlib import Path

import urgap


def test_execute_threaded_function_nested_args():
    arg_list = [
        ("One Ring to rule them all.", r"One Ring"),
        ("The War of the Ring lasted from TA 3018 to TA 3019.", r"TA \d{4}"),
        ("One Ring to find them.", r"to rule them all"),
    ]
    result = urgap.util.execute_threaded_function(
        urgap.util.extract_from_string,
        arg_list,
    )
    assert len(result) == 3
    assert ["One Ring"] and ["TA 3018", "TA 3019"] and [] in result


def test_execute_threaded_function_flat_args(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data/compressions")
    ufl = urgap.UFileList.from_folder(base_folder)
    urgap.util.execute_threaded_function(urgap.UFile.download, ufl)
    for uf in ufl:
        assert uf.path.exists()
