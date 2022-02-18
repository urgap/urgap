


def test_list_of_Ufiles_is_returned(tmp_file):
    input_files = [
    ]
    assert flat_input_files == input_files


def test_list_of_nested_Ufiles_is_returned(tmp_file):
    expected = [
    ]
    input_files = [
    ]
    assert flat_input_files == expected


def test_non_ufile_input_raises_TypeError(tmp_file):
    with pytest.raises(TypeError):


def test_more_than_1_level_nesting_raises_type_error(tmp_file):
    with pytest.raises(TypeError):
                [
                    [
                    ],
                ],