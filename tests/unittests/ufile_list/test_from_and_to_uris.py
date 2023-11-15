

def test_init_by_uri_string():
    uri_list = [
    ]
    assert ufile_list[0].tags is not None
    uri_list_re_created = ufile_list.as_uri_list()
    assert sorted(uri_list) == sorted(uri_list_re_created)