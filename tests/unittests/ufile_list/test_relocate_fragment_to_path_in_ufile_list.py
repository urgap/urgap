import urgap


def test_relocate_fragment_bigger_fragment():
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
    ufl.relocate_fragment_to_path(steps=-2)
    assert (
        ufl[0].uri
        == f"file:///this/test?uftype={urgap.uftypes.any.TXT}#works/data/test_node_data/sub/folder/test.txt"
    )
    assert ufl[0].uuri.path == "/this/test"
    assert ufl[0].uuri.fragment == "works/data/test_node_data/sub/folder/test.txt"

    assert (
        ufl[1].uri
        == f"file:///this/test/works/data?uftype={urgap.uftypes.any.TXT}#test_node_data/sub/folder/test.txt"
    )
    assert ufl[1].uuri.path == "/this/test/works/data"
    assert ufl[1].uuri.fragment == "test_node_data/sub/folder/test.txt"


def test_relocate_fragment_bigger_fragment_with_query_more_than_once():
    ufl = urgap.UFileList(
        [
            urgap.UFile(
                uri=f"file:///this/test/works/data?md5=random123456bytes&uftype={urgap.uftypes.any.TXT}#test_node_data/sub/folder/test.txt"
            ),
            urgap.UFile(
                uri=f"file:///this/test/works/data/test_node_data/sub?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#folder/test.txt"
            ),
        ]
    )
    ufl.relocate_fragment_to_path(steps=-2)
    assert (
        ufl[0].uri
        == f"file:///this/test?md5=random123456bytes&uftype={urgap.uftypes.any.TXT}#works/data/test_node_data/sub/folder/test.txt"
    )
    assert ufl[0].uuri.path == "/this/test"
    assert ufl[0].uuri.fragment == "works/data/test_node_data/sub/folder/test.txt"
    assert ufl[0].uftype == urgap.uftypes.any.TXT
    assert ufl[0].hash == "random123456bytes"

    assert (
        ufl[1].uri
        == f"file:///this/test/works/data?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#test_node_data/sub/folder/test.txt"
    )
    assert ufl[1].uuri.path == "/this/test/works/data"
    assert ufl[1].uuri.fragment == "test_node_data/sub/folder/test.txt"
    assert ufl[1].uftype == urgap.uftypes.any.CSV
    assert ufl[1].hash == "random123bytes"

    ufl.relocate_fragment_to_path(steps=3)
    assert (
        ufl[0].uri
        == f"file:///this/test/works/data/test_node_data?md5=random123456bytes&uftype={urgap.uftypes.any.TXT}#sub/folder/test.txt"
    )
    assert ufl[0].uuri.path == "/this/test/works/data/test_node_data"
    assert ufl[0].uuri.fragment == "sub/folder/test.txt"
    assert ufl[0].uftype == urgap.uftypes.any.TXT
    assert ufl[0].hash == "random123456bytes"

    assert (
        ufl[1].uri
        == f"file:///this/test/works/data/test_node_data/sub/folder?md5=random123bytes&uftype={urgap.uftypes.any.CSV}#test.txt"
    )
    assert ufl[1].uuri.path == "/this/test/works/data/test_node_data/sub/folder"
    assert ufl[1].uuri.fragment == "test.txt"
    assert ufl[1].uftype == urgap.uftypes.any.CSV
    assert ufl[1].hash == "random123bytes"
