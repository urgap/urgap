import json
from pathlib import Path



def test_create_home_folder(tmp_dir):


def test_copy_resources_if_needed(tmp_dir):
    assert (
        Path(
        ).exists()
        is True
    )


def test_copy_resources_if_needed_fails_due_to_md5_mismatch(tmp_dir):

    file = Path(f"{tmp_dir}/resources/TestNodes/TestNode1/1_0_0/test_resource_1.py")
    assert file.exists() is True
    with open(file, "w") as f:
        f.write("New Content")

    assert md5 != md5_new_content
    assert md5_new_content == md5_second_push


def test_copy_config_if_needed(tmp_dir):


def test_read_config(tmp_dir):
        json.dump({"umeta": {"value": "dummy"}}, fp, indent=4)
    assert "umeta" in _config.keys()


def test_scratch_disk_base_has_uwid():