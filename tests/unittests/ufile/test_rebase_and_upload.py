#!/usr/bin/env python
import tempfile

from pathlib import Path

import urgap


def test_rebase_and_upload(tmpdir):
    file = urgap.UFile.from_path_object(
        path_object=Path(f"{urgap._test_folder}/data/usermods/usermods.xml"),
        query=f"uftype={urgap.uftypes.proteomics.MODS_XML}",
    )
    file.rebase(f"file://{tmpdir}/data/test_node_data")
    file.upload()
    assert Path(f"{tmpdir}/data/test_node_data/usermods/usermods.xml").exists()


def test_rename_object_name():
    with tempfile.TemporaryDirectory() as _temp_directory:
        source_object_name = "object.txt"
        source_subfolder_structure = "level_1/level_2"
        source_folder = Path(_temp_directory) / Path(source_subfolder_structure)
        source_folder.mkdir(parents=True, exist_ok=True)

        source_object = source_folder / source_object_name
        with open(source_object, "w") as oo:
            print("___--->>>", file=oo)

        source_ufile = urgap.UFile(
            uri=f"file://{_temp_directory}#{source_subfolder_structure}/{source_object_name}",
        )
        new_subfolder_structure = "level_3"
        new_object_name = "obj3ct.txt"
        source_ufile.rebase(
            f"#{new_subfolder_structure}/{new_object_name}",
            upload=True,
        )
        _theoretical_path = (
            Path(_temp_directory) / Path(new_subfolder_structure) / new_object_name
        )
        assert _theoretical_path.exists() is True
        with open(_theoretical_path) as f:
            assert f.readline().strip() == "___--->>>"