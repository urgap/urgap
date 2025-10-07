import urgap


    uf = urgap.UFile("mylabdata://some/bucket/in/mld#some/file.txt")
    assert uf.uuri.get_mylabdata_api_url_files() == "https://some/files"
    assert uf.uuri.mylabdata_url == "https://some/files/bucket/in/mld/some%2Ffile.txt"

    uf2 = urgap.UFile("mylabdata://some/bucket/in/mld#some/filewith#.txt")
    assert (
        uf2.uuri.mylabdata_url
        == "https://some/files/bucket/in/mld/some%2Ffilewith%23.txt"
    )

    uf3 = urgap.UFile("mylabdata://some/bucket/in/mld#some/file with spaces/#=4.txt")
    assert (
        uf3.uuri.mylabdata_url
        == "https://some/files/bucket/in/mld/some%2Ffile%20with%20spaces%2F%23%3D4.txt"
    )