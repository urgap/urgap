

def test_wrapper_compress_to_tar(tmp_dir):
    )
        {
            "parameters": {"CompressToTar:1.0.0": {}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    result_tar = CompressToTar_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert result_tar[0].path.exists()
    assert result_tar[0].path.suffix == ".tar"
    result_ufl = result_tar[0].uncompress()
    assert result_ufl.all_remote_files_exist
    assert len(ufiles) == len(result_ufl) - 1  # due to recursive untar


def test_wrapper_compress_to_tar_max_size(tmp_dir):
    )
        {
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
            },
    )
    result_tar = CompressToTar_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert len(result_tar) == 2
    assert result_tar[0].path.exists()
    assert result_tar[0].path.suffix == ".tar"
    result_ufl = result_tar[0].uncompress()
    assert result_ufl.all_remote_files_exist
    assert len(ufiles) == len(result_ufl) - 1  # due to recursive untar


def test_wrapper_compress_to_tar_latest(tmp_dir):
    )
        {
            "parameters": {"CompressToTar:latest": {}},
            "unode_parameters": {
                "storage_base_uri": f"file://{tmp_dir}",
                "latest_exe_paths": {
                    / "resources"
                    / "Compressor"
                    / "1_0_0"
                },
            },
    )
    result_tar = CompressToTar_node.run(urun_dict=urun_dict, ufiles=ufiles)
    assert result_tar[0].path.exists()
    assert result_tar[0].path.suffix == ".tar"
    result_ufl = result_tar[0].uncompress()
    assert result_ufl.all_remote_files_exist
    assert len(ufiles) == len(result_ufl) - 1  # due to recursive untar