import pytest

import urgap


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "TestNode5:1.0.0": {
                            urgap.uftypes.test.TEST_FILE1: 1,
                            urgap.uftypes.test.TEST_FILE2: 1,
                            urgap.uftypes.test.MITSURUGI: 3,
                        },
                    },
                    "unode_parameters": {
                        "force": True,
                    },
                },
            ),
            ["TestNode5:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_can_query_node_outputs_by_aliases(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    test_node9 = test_nodes["TestNode5:1.0.0"]
    results = test_node9.run(ufiles=ufiles, urun_dict=urun_dict)

    pac_id, wid = test_node9.utrace_history[-1]
    report = urgap.UReport(wid=wid, storage_base_uri=results[0].as_storage_base_uri())
    report.draw_execution_dag()
    queried_results = report.query_node_outputs_by_aliases(nodes={0: []})
    assert set(uf.ucfs for uf in queried_results) == {uf.ucfs for uf in results.data}


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.test.TEST_FILE2}#"
                f"test_node_data/test.txt",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "TestNode5:1.0.0": {
                            urgap.uftypes.test.TEST_FILE1: 1,
                            urgap.uftypes.test.TEST_FILE2: 1,
                            urgap.uftypes.test.MITSURUGI: 3,
                        },
                    },
                },
            ),
            ["TestNode5:1.0.0"],
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_provides_only_specified_uftype(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    test_node9 = test_nodes["TestNode5:1.0.0"]
    results = test_node9.run(ufiles=ufiles, urun_dict=urun_dict)

    pac_id, wid = test_node9.utrace_history[-1]
    report = urgap.UReport(wid=wid, storage_base_uri=results[0].as_storage_base_uri())
    report.draw_execution_dag()
    queried_results = report.query_node_outputs_by_aliases(
        nodes={0: [urgap.uftypes.test.MITSURUGI]},
    )
    filtered_results = []
    for i in results.get_indices_by_uftype(urgap.uftypes.test.MITSURUGI):
        filtered_results.append(results[i])
    filtered_results = urgap.UFileList(filtered_results)
    for i, ufile in enumerate(queried_results.data):
        assert ufile.object_name == filtered_results.data[i].object_name


@pytest.mark.parametrize(
    "provide_clean_node_dirs",
    [
        (
            urgap.UFile(
                uri=f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.genomics.plink.BIM}"
                f"#unified_csvs/demo.csv",
            ),
            urgap.URunDict(
                {
                    "parameters": {
                        "FilterTabularToCSV:1.0.0": {
                            "-q": "`spectrum_id` > 3000",
                        },
                    },
                    "unode_parameters": {
                        "force": True,
                    },
                },
            ),
            ["FilterTabularToCSV:1.0.0"],
        ),
    ],
    indirect=["provide_clean_node_dirs"],
)
def test_can_discriminate_aliases(provide_clean_node_dirs, tmp_dir):
    test_nodes, ufiles, urun_dict = provide_clean_node_dirs
    urun_dict["unode_parameters"].update({"storage_base_uri": f"file://{tmp_dir}"})
    test_node = test_nodes["FilterTabularToCSV:1.0.0"]
    results = test_node.run(ufiles=ufiles, urun_dict=urun_dict)
    urun_dict.parameters["FilterTabularToCSV:1.0.0"]["-q"] = "`spectrum_id` < 3100"
    results_with_less = test_node.run(ufiles=results, urun_dict=urun_dict, force=True)

    pac_id, wid = test_node.utrace_history[-1]
    report = urgap.UReport(
        wid=wid,
        storage_base_uri=results_with_less[0].as_storage_base_uri(),
    )
    report.draw_execution_dag()
    queried_results = report.query_node_outputs_by_aliases(nodes={0: []})
    queried_results_with_less = report.query_node_outputs_by_aliases(nodes={2: []})
    queried_results_combined = report.query_node_outputs_by_aliases(
        nodes={0: [], 2: []},
    )
    assert results == queried_results
    assert results_with_less == queried_results_with_less
    assert len(results) + len(results_with_less) == len(queried_results_combined)
    results.append(results_with_less[0])
    assert queried_results_combined == results
