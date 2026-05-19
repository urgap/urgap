#!/usr/bin/env python3
import pytest

import urgap


def test_wrapper_pymzml2mgf_2_6_simple(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML}#ms_files/BSA1.mzML"
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "PymzMLToMGF:2.6.0": {},
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        }
    )
    node = urgap.init_unode("PymzMLToMGF:2.6.0")
    output_files = node.run(
        ufiles,
        urun_dict,
    )
    assert output_files[0].path.exists() is True
    with open(output_files[0].path, "r") as test_file:
        lines = [l for l in test_file]
        assert len(lines) == 133179


def test_wrapper_pymzml2mgf_2_6_param(tmp_dir):
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype="
                f"{urgap.uftypes.ms.converter.mzml.THERMORAWPARSER_MZML}#ms_files/BSA1.mzML"
            ),
        ],
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {
                "PymzMLToMGF:2.6.0": {
                    "-s": 10,
                },
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        }
    )
    node = urgap.init_unode("PymzMLToMGF:2.6.0")
    output_files = node.run(
        ufiles,
        urun_dict,
    )
    assert output_files[0].path.exists() is True
    with open(output_files[0].path, "r") as test_file:
        lines = [l for l in test_file]
        assert len(lines) == 13629
