from pathlib import Path

import pytest



def test_filtering_on_single_file_(tmp_scratch_disk):

    )

    filtered_list = ufl.filter(
    )
    assert filtered_list == [uf]


def test_filtering_on_two_files_one_excluding(tmp_scratch_disk):

    )
    )

    filtered_list = ufl.filter(
        input_uftypes={
        },
    )
    assert filtered_list == [uf_1]


def test_filtering_on_two_files_one_excluding_based_on_additional_filters(
    tmp_scratch_disk,
):

    )
    )

    filtered_list = ufl.filter(
        input_uftypes={},
        additional_filters={
        },
    )
    assert filtered_list == [uf_2]


def test_filtering_on_single_file_with_minium_zero(tmp_scratch_disk):

    )

    filtered_list = ufl.filter(
        input_uftypes={
        },
    )
    assert filtered_list == []


def test_filtering_on_single_file_with_minium_zero_one_incl(tmp_scratch_disk):

    )

    filtered_list = ufl.filter(
        input_uftypes={
        },
    )
    assert filtered_list == [uf_1]


def test_wrapper_definitions_are_met(tmp_scratch_disk):
    ufiles = [
        ),
        ),
        ),
    ]

    filtered_list = ufl.filter(
        input_uftypes={
    )

    assert len(filtered_list) == 3


def test_wrapper_definitions_are_met_max(tmp_scratch_disk):
    ufiles = [
        ),
        ),
        ),
        ),
        ),
    ]

    filtered_list = ufl.filter(
        input_uftypes={
    )

    assert len(filtered_list) == 5


def test_wrapper_defintions_are_met_with_additional_filters(tmp_scratch_disk):
    ufiles = [
        ),
        ),
        ),
        ),
        ),
    ]

    filtered_list = ufl.filter(
        input_uftypes={
        },
    )
    assert len(filtered_list) == 3


def test_wrapper_defintions_are_met_with_additional_filters_nested_structure(
    tmp_scratch_disk,
):
    ufiles = [
        ),
        [
            ),
            ),
        ],
        [
            ),
            ),
        ],
    ]

    filtered_list = ufl.filter(
        input_uftypes={
        },
    )
    assert len(filtered_list) == 3


def test_wrapper_defintions_are_not_met_with_additional_filters(tmp_scratch_disk):
    ufiles = [
        ),
        ),
        ),
        ),
        ),
    ]


    with pytest.raises(ValueError):
            input_uftypes={
            },
            additional_filters={
            },
        )


def test_filter_ufile_list_too_many_files(tmp_dir):
    ufiles = (
            [
                ),
                ),
        ),
    )
        {
            "parameters": {
                "BasicFunctionTestNode:1.1.0": {
                    "triggers_nuttin": 100,
                    "triggers_rerun": 100,
                    "triggers_rerun_-3": 100,
            },
            "unode_parameters": {
                "record_skipped_runs": True,
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )

    with pytest.raises(ValueError):