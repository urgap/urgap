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
                {
                    "parameters": {
                    },
            ),
        ),
    ],
    indirect=["provide_clean_test_node_dirs"],
)
def test_provides_only_specified_uftype(provide_clean_test_node_dirs):
    test_nodes, ufiles, urun_dict = provide_clean_test_node_dirs
    results = test_node9.run(ufiles=ufiles, urun_dict=urun_dict)

    report.draw_execution_dag()
    queried_results = report.query_node_outputs_by_aliases(
    )
    filtered_results = []
        filtered_results.append(results[i])
        assert ufile.object_name == filtered_results.data[i].object_name


@pytest.mark.parametrize(
    "provide_clean_node_dirs",
    [
        (
            ),
                {
                    "parameters": {
                    },
                    "unode_parameters": {
                        "force": True,
                    },
            ),
    ],
    indirect=["provide_clean_node_dirs"],
)
    test_nodes, ufiles, urun_dict = provide_clean_node_dirs
    results = test_node.run(ufiles=ufiles, urun_dict=urun_dict)

    report.draw_execution_dag()
    queried_results = report.query_node_outputs_by_aliases(nodes={0: []})
    queried_results_with_less = report.query_node_outputs_by_aliases(nodes={2: []})
    queried_results_combined = report.query_node_outputs_by_aliases(
    )
    assert results == queried_results
    assert results_with_less == queried_results_with_less
    assert len(results) + len(results_with_less) == len(queried_results_combined)