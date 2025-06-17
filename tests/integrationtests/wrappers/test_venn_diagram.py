"""Integration test for VennDiagram."""



        [
    )
        {
            "parameters": {
                "VennDiagram:2.0.0": {
                    "--id-column": ["charge"],
                    "--value-column": ["sequence"],
            },
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    venn_svg = venn_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert venn_svg[0].path.exists()