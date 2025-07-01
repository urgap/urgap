"""Integration test for VennDiagram."""

import re

import urgap


def test_wrapper_venn_diagram(tmp_dir: urgap.Path) -> None:  # noqa: D103
    ufiles = urgap.UFileList(
        [
            urgap.UFile(
    )
    urun_dict = urgap.URunDict(
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
    venn_node = urgap.init_unode("VennDiagram:2.0.0")
    venn_svg = venn_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert venn_svg[0].path.exists()
    with open(venn_svg[0].path) as svg_file:
        svg_content = svg_file.read()
    # all_true =
    assert all(
        bool(re.search(pattern, svg_content, re.DOTALL))
        for pattern in expected_patterns_svg
    )