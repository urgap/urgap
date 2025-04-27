from click.testing import CliRunner


runner = CliRunner()




    runner.invoke(describe_wid_click, ["test_wid"])


    runner.invoke(describe_node_ex_id_click, ["BasicFunctionTestNode:1.1.0"])