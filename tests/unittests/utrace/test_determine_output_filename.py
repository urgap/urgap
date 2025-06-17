import random
import re



def test_single_input():
        [
            ),
        ],
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()
    assert (
        bool(
            re.search(
                r"TestNode4_1.0.0_wx_[0-9a-z]{32}/b8dd6ef5f15f638b208bc7c28df13a19",
                _output,
            ),
        )
        is True
    )


def test_single_input_no_data_versioning():
        [
            ),
        ],
    )
        {
            "parameters": {},
            "unode_parameters": {
                "skip_data_versioning": True,
            },
        },
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()

    assert (
        bool(re.search(r"TestNode4_1.0.0_wx/b8dd6ef5f15f638b208bc7c28df13a19", _output))
        is True
    )


def test_single_input_with_run_folder_name():
        [
            ),
        ],
    )
        {
            "parameters": {},
            "unode_parameters": {
                "run_folder_name": "MoRunFolder",
            },
        },
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()

    assert (
        bool(
            re.search(
                r"MoRunFolder_[0-9a-z]{32}/b8dd6ef5f15f638b208bc7c28df13a19",
                _output,
            ),
        )
        is True
    )


def test_single_input_with_prefix_and_nested_dir():
        [
            ),
        ],
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()
    assert (
        bool(
            re.search(
                "TestNode4_1.0.0_wx_[0-9a-z]{32}/_!_b8dd6ef5f15f638b208bc7c28df13a19",
                str(_output),
            ),
        )
        is True
    )


def test_single_input_with_data_versioning():
        [
            ),
        ],
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()
    assert (
        bool(
            re.search(
                r"TestNode4_1.0.0_wx_"
                str(_output),
            ),
        )
        is True
    )


def test_multi_input():
        [
            ),
            ),
            ),
        ],
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()
    assert (
        bool(
            re.search(
                r"TestNode4_1.0.0_wx_[0-9a-z]{32}/9dbda1cf7a25c9e8da2b4e7d60be1387",
                str(_output),
            ),
        )
        is True
    )


def test_multi_input_shuffled_input():
    pre_list = [
        ),
        ),
        ),
    ]
    random.shuffle(pre_list)
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()
    assert (
        bool(
            re.search(
                r"TestNode4_1.0.0_wx_[0-9a-z]{32}/9dbda1cf7a25c9e8da2b4e7d60be1387",
                str(_output),
            ),
        )
        is True
    )


def test_multi_input_with_data_versioning():
        [
            ),
            ),
            ),
        ],
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()
    assert (
        bool(
            re.search(
                r"TestNode4_1.0.0_wx_[0-9a-z]{32}/9dbda1cf7a25c9e8da2b4e7d60be1387",
                str(_output),
            ),
        )
        is True
    )
    assert (
        bool(
            re.search(
                r"TestNode4_1.0.0_wx_"
                str(_output),
            ),
        )
        is True
    )


def test_override_folder_creation_with_md5():
        [
            ),
            ),
            ),
        ],
    )
        urun_dict=urd,
        input_files=input_files,
    )
    _output = ut.determine_output_files_stem()
    assert _output == "9dbda1cf7a25c9e8da2b4e7d60be1387"