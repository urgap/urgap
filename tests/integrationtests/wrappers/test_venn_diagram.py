"""Integration test for VennDiagram."""

import re



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
    expected_patterns_svg = [
        r"<text[^>]*?>.*?n = 39.*?</text>",
        r"<text[^>]*?>.*?n = 16.*?</text>",
        r"<text[^>]*?>.*?n = 28.*?</text>",
        r"<text[^>]*?>.*?n = 17.*?</text>",
    ]
    venn_svg = venn_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert venn_svg[0].path.exists()
    with open(venn_svg[0].path) as svg_file:
        svg_content = svg_file.read()
    assert all(
    )