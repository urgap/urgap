import urgap


def test_init_by_uri_string():
    uri_list = [
        "file://{urgap._test_folder}/data?uftype=.any.csv#unified_csvs/test.csv",
        "file://{urgap._test_folder}/data?uftype=.any.csv#unified_csvs/demo.csv",
    ]
    ufile_list = urgap.UFileList.from_uri_list(uri_list)
    assert isinstance(ufile_list[0], urgap.UFile)
    assert ufile_list[0].tags is not None
