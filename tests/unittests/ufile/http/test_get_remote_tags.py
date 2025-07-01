import urgap

remote_url = "https://raw.githubusercontent.com/computational-ms/demo_files/main/ursgal_resources"


def test_get_remote_tags_omssa_2_1_9():
    node_urn = "darwin/arm64/omssa_2_1_9.zip"
    ufile = urgap.UFile(uri=f"{remote_url}#{node_urn}")
    remote_tag = ufile.io.get_remote_tags()
    assert remote_tag["md5"] == "403e1f1245f8e4a73ffedcd33c5d2c51"


def test_get_remote_tags_test_node_v8():
    node_urn = "linux/x86_64/test_node_v8.zip"
    ufile = urgap.UFile(uri=f"{remote_url}#{node_urn}")
    remote_tag = ufile.io.get_remote_tags()
    assert remote_tag["md5"] == "1fbb335b02cbc552bc0302bbc7f83a0a"
    assert "note" in remote_tag.keys()


def test_get_remote_tags_no_file():
    node_urn = "None"
    ufile = urgap.UFile(uri=f"{remote_url}#{node_urn}")
    remote_tag = ufile.io.get_remote_tags()
    assert remote_tag is None


def test_get_remote_tags_no_tags_but_response():
    ufile = urgap.UFile(
        uri="https://github.com/gsk-tech/pymx/raw/main/example_scripts"
        "#filter_nonbiological_ions_1_0_0.py",
    )
    remote_tag = ufile.io.get_remote_tags()
    assert remote_tag is None