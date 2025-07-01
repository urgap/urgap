import json

from pathlib import Path

import urgap


def test_create_home_folder(tmp_dir):
    urgap.uinit.create_home_folder(home_dir_parent=tmp_dir)
    assert Path(tmp_dir / ".urgap").exists() is True


def test_copy_resources_if_needed(tmp_dir):
    urgap.uinit.copy_resources_if_needed(target_dir=tmp_dir)
    assert (
        Path(
            f"{tmp_dir}/resources/TestNodes/TestNode1/1_0_0/test_resource_1.py",
        ).exists()
        is True
    )


def test_copy_resources_if_needed_fails_due_to_md5_mismatch(tmp_dir):
    urgap.uinit.copy_resources_if_needed(target_dir=tmp_dir)

    file = Path(f"{tmp_dir}/resources/TestNodes/TestNode1/1_0_0/test_resource_1.py")
    md5 = urgap.ucore.calculate_file_hash(file, hash_algorithm="md5")
    assert file.exists() is True
    with open(file, "w") as f:
        f.write("New Content")

    md5_new_content = urgap.ucore.calculate_file_hash(file, hash_algorithm="md5")
    urgap.uinit.copy_resources_if_needed(target_dir=tmp_dir)
    md5_second_push = urgap.ucore.calculate_file_hash(file, hash_algorithm="md5")
    assert md5 != md5_new_content
    assert md5_new_content == md5_second_push


def test_copy_config_if_needed(tmp_dir):
    urgap.uinit.copy_config_if_needed(target_dir=tmp_dir)
    assert Path(tmp_dir / "urgap.json").exists() is True


def test_read_config(tmp_dir):
    with open(Path(tmp_dir) / "urgap.json", "w") as fp:
        json.dump({"umeta": {"value": "dummy"}}, fp, indent=4)
    _config = urgap.uinit.read_config(home_dir=tmp_dir)
    assert "umeta" in _config.keys()


def test_scratch_disk_base_has_uwid():
    assert urgap.scratch_disk_base.name == urgap.session_uwid