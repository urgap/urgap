import pytest

@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
            ),
                {
                    "parameters": {
                    },
            ),
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_can_query_node_outputs_by_aliases(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    results = test_node9.run(ufiles=ufiles, urun_dict=urun_dict)

    report.draw_execution_dag()
    queried_results = report.query_node_outputs_by_aliases(nodes={0: []})


@pytest.mark.parametrize(
    "provide_clean_test_node_dirs",
    [
        (
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_provides_only_specified_uftype(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    results = test_node9.run(ufiles=ufiles, urun_dict=urun_dict)

    report.draw_execution_dag()
    filtered_results = []
        filtered_results.append(results[i])

@pytest.mark.parametrize(
    "provide_clean_node_dirs",
    [
        (
    ],
    indirect=["provide_clean_node_dirs"],
)
    test_nodes, ufiles, urun_dict = provide_clean_node_dirs
    results = test_node.run(ufiles=ufiles, urun_dict=urun_dict)

    report.draw_execution_dag()
    queried_results = report.query_node_outputs_by_aliases(nodes={0: []})
    assert results == queried_results
    assert results_with_less == queried_results_with_less