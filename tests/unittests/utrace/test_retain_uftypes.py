#!/usr/bin/env python
import pandas as pd


pd.set_option("display.max_columns", 100)


def test_retain_uftype_all_same_not_set():
        [
            ),
            ),
    )
        {
            "parameters": {
                "pandas_query_string": "`Sequence` == `Sequence`",
            },
    )
        urun_dict=urd,
        input_files=input_files,
    )
    assert ut.output_files[0].tags.get("uftype", None) == ".any.csv"


def test_retain_uftype_all_same():
        [
            ),
            ),
    )
        {
            "parameters": {
                "pandas_query_string": "`Sequence` == `Sequence`",
            },
            "unode_parameters": {"retain_uftype": True},
    )
        urun_dict=urd,
        input_files=input_files,
    )

    # First check the scans_file
    assert (
        ut.output_files[0].tags.get("uftype", None)
    )


def test_retain_uftype_different():
        [
            ),
            ),
    )
        {
            "parameters": {
                "pandas_query_string": "`Sequence` == `Sequence`",
            },
            "unode_parameters": {"retain_uftype": True},
    )
        urun_dict=urd,
        input_files=input_files,
    )
    assert ut.output_files[0].tags.get("uftype", None) == ".any.csv"