from pathlib import Path

import pytest

import urgap


def test_filtering_on_single_file_(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    ufl = urgap.UFileList([uf])

    filtered_list = ufl.filter(
        input_uftypes={urgap.uftypes.test.TEST_FILE1: {"min": 1, "max": 3}},
    )
    assert filtered_list == [uf]


def test_filtering_on_two_files_one_excluding(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf_1 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    uf_2 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE2}#test_2.txt",
    )

    ufl = urgap.ufile_list.UFileList([uf_1, uf_2])
    filtered_list = ufl.filter(
        input_uftypes={
            urgap.uftypes.test.TEST_FILE1: {"min": 1, "max": 3},
        },
    )
    assert filtered_list == [uf_1]


def test_filtering_on_two_files_one_excluding_based_on_additional_filters(
    tmp_scratch_disk,
):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf_1 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )
    uf_2 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE2}&QC=good#test_2.txt",
    )

    ufl = urgap.ufile_list.UFileList([uf_1, uf_2])
    filtered_list = ufl.filter(
        input_uftypes={},
        additional_filters={
            urgap.uftypes.test.TEST_FILE2: {"tags": {"QC": "good"}},
        },
    )
    assert filtered_list == [uf_2]


def test_filtering_on_single_file_with_minium_zero(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf_1 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_1.txt",
    )

    ufl = urgap.ufile_list.UFileList([uf_1])
    filtered_list = ufl.filter(
        input_uftypes={
            urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 3},
        },
    )
    assert filtered_list == []


def test_filtering_on_single_file_with_minium_zero_one_incl(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()

    uf_1 = urgap.UFile(
        uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
    )

    ufl = urgap.ufile_list.UFileList([uf_1])
    filtered_list = ufl.filter(
        input_uftypes={
            urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 3},
        },
    )
    assert filtered_list == [uf_1]


def test_wrapper_definitions_are_met(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    filtered_list = ufl.filter(
        input_uftypes={
            urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 3},
            urgap.uftypes.test.MITSURUGI: {"min": 2, "max": 4},
        },
    )

    assert len(filtered_list) == 3


def test_wrapper_definitions_are_met_max(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_4.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_5.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    filtered_list = ufl.filter(
        input_uftypes={
            urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 3},
            urgap.uftypes.test.MITSURUGI: {"min": 2, "max": 4},
        },
    )

    assert len(filtered_list) == 5


def test_wrapper_defintions_are_met_with_additional_filters(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}&qc=good#test_4.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}&qc=good#test_5.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    filtered_list = ufl.filter(
        input_uftypes={
            urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 3},
            urgap.uftypes.test.MITSURUGI: {"min": 2, "max": 4},
        },
        additional_filters={urgap.uftypes.test.MITSURUGI: {"tags": {"qc": "good"}}},
    )
    assert len(filtered_list) == 3


def test_wrapper_defintions_are_met_with_additional_filters_nested_structure(
    tmp_scratch_disk,
):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        [
            urgap.UFile(
                uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}&qc=good#test_2.txt",
            ),
            urgap.UFile(
                uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
            ),
        ],
        [
            urgap.UFile(
                uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_4.txt",
            ),
            urgap.UFile(
                uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}&qc=good#test_5.txt",
            ),
        ],
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)
    filtered_list = ufl.filter(
        input_uftypes={
            urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 3},
            urgap.uftypes.test.MITSURUGI: {"min": 2, "max": 4},
        },
        additional_filters={urgap.uftypes.test.MITSURUGI: {"tags": {"qc": "good"}}},
    )
    assert len(filtered_list) == 3


def test_wrapper_defintions_are_not_met_with_additional_filters(tmp_scratch_disk):
    base_folder = Path(f"{urgap._test_folder}/data").resolve()
    ufiles = [
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.TEST_FILE1}#test_1.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_2.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_3.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}#test_4.txt",
        ),
        urgap.UFile(
            uri=f"file://{base_folder}?uftype={urgap.uftypes.test.MITSURUGI}&qc=good#test_5.txt",
        ),
    ]

    ufl = urgap.ufile_list.UFileList(ufiles)

    with pytest.raises(ValueError):
        ufl.filter(
            input_uftypes={
                urgap.uftypes.test.TEST_FILE1: {"min": 0, "max": 3},
                urgap.uftypes.test.MITSURUGI: {"min": 2, "max": 4},
            },
            additional_filters={
                urgap.uftypes.test.MITSURUGI: {"tags": {"qc": "good"}},
            },
        )


def test_filter_ufile_list_too_many_files(tmp_dir):
    ufiles = (
        urgap.UFileList(
            [
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}#"
                    f"test_node_data/test.txt",
                ),
                urgap.UFile(
                    uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE1}"
                    f"#unified_csvs/demo.csv",
                ),
            ],
        ),
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "BasicFunctionTestNode:1.1.0": {
                    "triggers_nuttin": 100,
                    "triggers_rerun": 100,
                    "triggers_rerun_-3": 100,
                },
            },
            "unode_parameters": {
                "record_skipped_runs": True,
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    test_node1 = urgap.init_unode("BasicFunctionTestNode:1.1.0")

    with pytest.raises(ValueError):
        test_node1.run(ufiles=ufiles, urun_dict=urun_dict)