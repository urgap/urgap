#!/usr/bin/env python
import pandas as pd

import urgap

pd.set_option("display.max_columns", 100)


def test_retain_uftype_all_same_not_set():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_abcdefg.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    urd = urgap.URunDict(
        {
            "parameters": {
                "pandas_query_string": "`Sequence` == `Sequence`",
            },
        },
    )
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_node("FilterTabularToCSV:1.0.0").META_INFO,
    )
    assert ut.output_files[0].tags.get("uftype", None) == ".any.csv"


def test_retain_uftype_all_same():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_abcdefg.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    urd = urgap.URunDict(
        {
            "parameters": {
                "pandas_query_string": "`Sequence` == `Sequence`",
            },
            "unode_parameters": {"retain_uftype": True},
        },
    )
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_node("FilterTabularToCSV:1.0.0").META_INFO,
    )

    # First check the scans_file
    assert (
        ut.output_files[0].tags.get("uftype", None)
        == urgap.uftypes.proteomics.converter.PYIOHAT_CSV
    )


def test_retain_uftype_different():
    input_files = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.proteomics.converter.PYIOHAT_CSV}#csvs"
                f"/sequence_abcdefg.csv",
            ),
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.any.CSV}#csvs"
                f"/sequence_defghij.csv",
            ),
        ],
    )
    urd = urgap.URunDict(
        {
            "parameters": {
                "pandas_query_string": "`Sequence` == `Sequence`",
            },
            "unode_parameters": {"retain_uftype": True},
        },
    )
    ut = urgap.UTrace(
        urun_dict=urd,
        input_files=input_files,
        unode_meta=urgap.init_node("FilterTabularToCSV:1.0.0").META_INFO,
    )
    assert ut.output_files[0].tags.get("uftype", None) == ".any.csv"
