import urgap


def test_relocate_fragment_bigger_fragment():
    uf = urgap.UFile(
        uri=f"file:///this/test/works/data#test_node_data/sub/folder/test.txt",
    )
    uf.relocate_fragment_to_path(steps=-2)
    assert uf.uri == "file:///this/test#works/data/test_node_data/sub/folder/test.txt"
    assert uf.uuri.path == "/this/test"
    assert uf.uuri.fragment == "works/data/test_node_data/sub/folder/test.txt"


def test_relocate_fragment_bigger_path():
    uf = urgap.UFile(
        uri=f"file:///this/test/works/data#test_node_data/sub/folder/test.txt",
    )
    uf.relocate_fragment_to_path(steps=2)
    assert uf.uri == "file:///this/test/works/data/test_node_data/sub#folder/test.txt"
    assert uf.uuri.path == "/this/test/works/data/test_node_data/sub"
    assert uf.uuri.fragment == "folder/test.txt"


def test_relocate_fragment_bigger_fragment_with_query():
    uf = urgap.UFile(
        uri=f"file:///this/test/works/data?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#test_node_data/sub/folder/test.txt",
    )
    uf.relocate_fragment_to_path(steps=-2)
    assert (
        uf.uri
        == f"file:///this/test?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#works/data/test_node_data/sub/folder/test.txt"
    )
    assert uf.uuri.path == "/this/test"
    assert uf.uuri.fragment == "works/data/test_node_data/sub/folder/test.txt"
    assert uf.uftype == urgap.uftypes.any.CSV
    assert uf.hash == "random123bytes"


def test_relocate_fragment_bigger_fragment_with_query_more_than_once():
    uf = urgap.UFile(
        uri=f"file:///this/test/works/data?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#test_node_data/sub/folder/test.txt",
    )
    uf.relocate_fragment_to_path(steps=-2)
    assert (
        uf.uri
        == f"file:///this/test?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#works/data/test_node_data/sub/folder/test.txt"
    )
    assert uf.uuri.path == "/this/test"
    assert uf.uuri.fragment == "works/data/test_node_data/sub/folder/test.txt"
    assert uf.uftype == urgap.uftypes.any.CSV
    assert uf.hash == "random123bytes"

    uf.relocate_fragment_to_path(steps=3)
    assert (
        uf.uri
        == f"file:///this/test/works/data/test_node_data?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#sub/folder/test.txt"
    )
    assert uf.uuri.path == "/this/test/works/data/test_node_data"
    assert uf.uuri.fragment == "sub/folder/test.txt"
    assert uf.uftype == urgap.uftypes.any.CSV
    assert uf.hash == "random123bytes"
