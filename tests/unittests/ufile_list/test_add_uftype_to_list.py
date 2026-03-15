import urgap


def test_add_uftype():
    ufl = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file:///this/test/works/data#test_node_data/sub/folder/test.txt"
            ),
            urgap.UFile(
                uri=f"file:///this/test/works/data/test_node_data/sub#folder/test.txt"
            ),
        ]
    )
    ufl.assign_uftype_to_ufiles(uftype=urgap.uftypes.any.CSV)
    for uf in ufl:
        assert uf.uftype == urgap.uftypes.any.CSV
        assert uf.tags["uftype"] == urgap.uftypes.any.CSV


def test_overwrite_uftype():
    ufl = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file:///this/test/works/data?uftype={urgap.uftypes.any.TXT}#test_node_data/sub/folder/test.txt"
            ),
            urgap.UFile(
                uri=f"file:///this/test/works/data/test_node_data/sub?uftype={urgap.uftypes.any.PDF}#folder/test.txt"
            ),
        ]
    )
    ufl.assign_uftype_to_ufiles(uftype=urgap.uftypes.any.CSV)
    for uf in ufl:
        assert uf.uftype == urgap.uftypes.any.CSV
        assert uf.tags["uftype"] == urgap.uftypes.any.CSV
