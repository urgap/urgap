import random
import string

import pytest



def _random_string(lenght=7):
    return "".join(random.choices(string.hexdigits, k=lenght))


def test_list_of_Ufiles_is_returned(tmp_file):
    input_files = [
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
    ]

        input_files,
    ).create_flat_and_non_redundant_list()
    assert flat_input_files == input_files


def test_list_of_nested_Ufiles_is_returned(tmp_file):
    expected = [
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
    ]
    input_files = [
        expected[0],
        [
            expected[1],
            expected[2],
        ],
        expected[3],
    ]
        input_files,
    ).create_flat_and_non_redundant_list()
    assert flat_input_files == expected


def test_non_ufile_input_raises_TypeError(tmp_file):
    with pytest.raises(TypeError):
            [
                "This string cannot not be an input!",
            ],
        ).create_flat_and_non_redundant_list()


def test_more_than_1_level_nesting_raises_type_error(tmp_file):
    with pytest.raises(TypeError):
            [
                [
                    [
                    ],
                ],
            ],
        ).create_flat_and_non_redundant_list()


def test_remove_redundancy_works(tmp_file):
    expected = [
    ]
    input_files = [
        [
        ],
    ]
        input_files,
    ).create_flat_and_non_redundant_list()
    assert flat_input_files == expected