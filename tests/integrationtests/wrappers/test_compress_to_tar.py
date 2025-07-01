import urgap


def test_wrapper_compress_to_tar(tmp_dir):
    ufiles = urgap.UFileList.from_folder(
        f"{urgap._test_folder}/data/compressions",
        uftype=urgap.uftypes.any.ANY,
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {"CompressToTar:1.0.0": {}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    CompressToTar_node = urgap.init_unode("CompressToTar:1.0.0")
    result_tar = CompressToTar_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert result_tar[0].path.exists()
    assert result_tar[0].path.suffix == ".tar"
    result_ufl = result_tar[0].uncompress()
    assert result_ufl.all_remote_files_exist
    assert len(ufiles) == len(result_ufl) - 1  # due to recursive untar


def test_wrapper_compress_to_tar_max_size(tmp_dir):
    ufiles = urgap.UFileList.from_folder(
        f"{urgap._test_folder}/data/compressions",
        uftype=urgap.uftypes.any.ANY,
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {"CompressToTar:1.0.0": {"-s": "25K"}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
        },
    )
    CompressToTar_node = urgap.init_unode("CompressToTar:1.0.0")
    result_tar = CompressToTar_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert len(result_tar) == 2
    assert result_tar[0].path.exists()
    assert result_tar[0].path.suffix == ".tar"
    result_ufl = result_tar[0].uncompress()
    assert result_ufl.all_remote_files_exist
    assert len(ufiles) == len(result_ufl) - 1  # due to recursive untar


def test_wrapper_compress_to_tar_latest(tmp_dir):
    ufiles = urgap.UFileList.from_folder(
        f"{urgap._test_folder}/data/compressions",
        uftype=urgap.uftypes.any.ANY,
    )
    urun_dict = urgap.URunDict(
        {
            "parameters": {"CompressToTar:latest": {}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    "CompressToTar:latest": urgap.home
                    / "resources"
                    / "Compressor"
                    / "1_0_0"
                    / "compressor.py",
                },
            },
        },
    )
    CompressToTar_node = urgap.init_unode("CompressToTar:latest")
    result_tar = CompressToTar_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert result_tar[0].path.exists()
    assert result_tar[0].path.suffix == ".tar"
    result_ufl = result_tar[0].uncompress()
    assert result_ufl.all_remote_files_exist
    assert len(ufiles) == len(result_ufl) - 1  # due to recursive untar