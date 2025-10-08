import pytest

import urgap


def test_node_fail_produces_none():
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                f"test_node_data/test.txt",
            ),
        ],
    )
    urun_dict = urgap.URunDict()
    test_node8 = urgap.init_node("TestNode8:1.0.0")
    result_8 = test_node8.run(
        ufiles=ufiles,
        urun_dict=urun_dict,
        force=True,
        crash_on_resource_crash=False,
    )
    assert None in result_8
    pac_id, wid = test_node8.utrace_history[-1]
    report = urgap.UReport(wid=wid)
    storage_base_uri = ufiles[0].storage_base_uri
    crashed_trace = report.get_trace(
        pac_id=pac_id,
        wid=wid,
        storage_base_uri=storage_base_uri,
    )
    assert crashed_trace.crashed is True


def test_node_fail_can_be_allowed():
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                f"test_node_data/test.txt",
            ),
        ],
    )
    urun_dict = urgap.URunDict()
    test_node8 = urgap.init_node("TestNode8:1.0.0")
    with pytest.raises(RuntimeError):
        test_node8.run(
            ufiles=ufiles,
            urun_dict=urun_dict,
            force=True,
            crash_on_resource_crash=True,
        )