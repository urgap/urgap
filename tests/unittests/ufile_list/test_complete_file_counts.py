

def test_complete_file_counts_single():
    )
    ufl.complete_file_counts()
    assert ufl[0].simple_name == "test_1_of_1"


def test_complete_file_counts_multiple():
    for i in range(1, 4):
        ufl.append(
        )
    ufl.complete_file_counts()
    assert set(uf.simple_name for uf in ufl) == {
        "test_1_of_3",
        "test_2_of_3",
        "test_3_of_3",
    }


def test_only_correct_are_set():
    for i in range(1, 4):
        ufl.append(
        )
    ufl.append(
    )
    ufl.append(
    )
    ufl.complete_file_counts()
    assert set(uf.simple_name for uf in ufl) == {
        "test_1_of_3",
        "test_2_of_3",
        "test_3_of_3",
        "different_1_of_1",
        "bait_1",
    }