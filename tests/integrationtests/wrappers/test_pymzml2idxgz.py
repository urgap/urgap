#!/usr/bin/env python3
import pytest
import pymzml
import urgap


def test_wrapper_PymzMLToIDXGZ(tmp_dir):
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
                "PymzMLToIDXGZ:2.6.0": {},
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        }
    )
    node = urgap.init_unode("PymzMLToIDXGZ:2.6.0")
    output_files = node.run(
        ufiles,
        urun_dict,
    )
    assert output_files[0].path.exists() is True
    ms_run = pymzml.run.Reader(output_files[0].path)
    assert ms_run[1337].ms_level == 1
