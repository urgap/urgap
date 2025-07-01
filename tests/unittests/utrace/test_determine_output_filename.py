import random
import re

import urgap


def test_single_input():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega",
            ),
        ],
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
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
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega",
            ),
        ],
    )
    urd = urgap.URunDict(
        {
            "parameters": {},
            "unode_parameters": {
                "skip_data_versioning": True,
            },
        },
    )
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
    )
    _output = ut.determine_output_files_stem()

    assert (
        bool(re.search(r"TestNode4_1.0.0_wx/b8dd6ef5f15f638b208bc7c28df13a19", _output))
        is True
    )


def test_single_input_with_run_folder_name():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega",
            ),
        ],
    )
    urd = urgap.URunDict(
        {
            "parameters": {},
            "unode_parameters": {
                "run_folder_name": "MoRunFolder",
            },
        },
    )
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
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
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega",
            ),
        ],
    )
    urd = urgap.URunDict({"unode_parameters": {"prefix": "_!_"}})
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
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
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega",
            ),
        ],
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
    )
    _output = ut.determine_output_files_stem()
    assert (
        bool(
            re.search(
                r"TestNode4_1.0.0_wx_"
                f"{ut.urun_dict.rerun_params_hash}"
                "/b8dd6ef5f15f638b208bc7c28df13a19",
                str(_output),
            ),
        )
        is True
    )


def test_multi_input():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega2",
            ),
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Cats/_.sega",
            ),
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zig/seriously.sega",
            ),
        ],
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
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
        urgap.UFile(
            f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega2",
        ),
        urgap.UFile(
            f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Cats/_.sega",
        ),
        urgap.UFile(
            f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zig/seriously.sega",
        ),
    ]
    random.shuffle(pre_list)
    input_files = urgap.UFileList(pre_list)
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
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
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega2",
            ),
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Cats/_.sega",
            ),
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zig/seriously.sega",
            ),
        ],
    )
    urd = urgap.URunDict()
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
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
                f"{ut.urun_dict.rerun_params_hash}"
                r"/[0-9a-z]{32}",
                str(_output),
            ),
        )
        is True
    )


def test_override_folder_creation_with_md5():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zero/Wing.sega2",
            ),
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Cats/_.sega",
            ),
            urgap.UFile(
                f"file://{urgap._test_folder}/data/?uftype={urgap.uftypes.any.ANY}#Zig/seriously.sega",
            ),
        ],
    )
    urd = urgap.URunDict({"unode_parameters": {"override_folder_creation": True}})
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_unode("TestNode4:1.0.0").META_INFO,
    )
    _output = ut.determine_output_files_stem()
    assert _output == "9dbda1cf7a25c9e8da2b4e7d60be1387"