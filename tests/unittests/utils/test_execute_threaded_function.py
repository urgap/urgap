from pathlib import Path



def test_execute_threaded_function_nested_args():
    arg_list = [
        ("One Ring to rule them all.", r"One Ring"),
        ("The War of the Ring lasted from TA 3018 to TA 3019.", r"TA \d{4}"),
        ("One Ring to find them.", r"to rule them all"),
    ]
        arg_list,
    )
    assert len(result) == 3
    assert ["One Ring"] and ["TA 3018", "TA 3019"] and [] in result


def test_execute_threaded_function_flat_args(tmp_scratch_disk):
    for uf in ufl:
        assert uf.path.exists()