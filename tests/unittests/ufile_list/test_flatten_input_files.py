import random
import string

import pytest

import urgap


def _random_string(lenght=7):
    return "".join(random.choices(string.hexdigits, k=lenght))


def test_list_of_Ufiles_is_returned(tmp_file):
    input_files = [
        urgap.UFile.from_path_object(
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
        urgap.UFile.from_path_object(
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
        urgap.UFile.from_path_object(
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
        urgap.UFile.from_path_object(
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
    ]

    flat_input_files = urgap.ufile_list.UFileList(
        input_files,
    ).create_flat_and_non_redundant_list()
    assert flat_input_files == input_files


def test_list_of_nested_Ufiles_is_returned(tmp_file):
    expected = [
        urgap.UFile.from_path_object(
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
        urgap.UFile.from_path_object(
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
        urgap.UFile.from_path_object(
            path_object=tmp_file.with_suffix(f".{_random_string()}"),
        ),
        urgap.UFile.from_path_object(
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
    flat_input_files = urgap.ufile_list.UFileList(
        input_files,
    ).create_flat_and_non_redundant_list()
    assert flat_input_files == expected


def test_non_ufile_input_raises_TypeError(tmp_file):
    with pytest.raises(TypeError):
        urgap.ufile_list.UFileList(
            [
                urgap.UFile.from_path_object(path_object=tmp_file),
                "This string cannot not be an input!",
            ],
        ).create_flat_and_non_redundant_list()


def test_more_than_1_level_nesting_raises_type_error(tmp_file):
    with pytest.raises(TypeError):
        urgap.ufile_list.UFileList(
            [
                urgap.UFile.from_path_object(path_object=tmp_file),
                [
                    urgap.UFile.from_path_object(path_object=tmp_file),
                    [
                        urgap.UFile.from_path_object(path_object=tmp_file),
                        urgap.UFile.from_path_object(path_object=tmp_file),
                    ],
                ],
                urgap.UFile.from_path_object(path_object=tmp_file),
            ],
        ).create_flat_and_non_redundant_list()


def test_remove_redundancy_works(tmp_file):
    expected = [
        urgap.UFile.from_path_object(path_object=tmp_file),
    ]
    input_files = [
        urgap.UFile.from_path_object(path_object=tmp_file),
        [
            urgap.UFile.from_path_object(path_object=tmp_file),
            urgap.UFile.from_path_object(path_object=tmp_file),
        ],
        urgap.UFile.from_path_object(path_object=tmp_file),
    ]
    flat_input_files = urgap.ufile_list.UFileList(
        input_files,
    ).create_flat_and_non_redundant_list()
    assert flat_input_files == expected