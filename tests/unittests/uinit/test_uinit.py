import json

def test_create_home_folder(tmp_dir):


    assert (
        Path(
        ).exists()
        is True
    )



        f.write("New Content")

    assert md5 != md5_new_content
    assert md5_new_content == md5_second_push


def test_copy_config_if_needed(tmp_dir):


def test_read_config(tmp_dir):
        json.dump({"umeta": {"value": "dummy"}}, fp, indent=4)
    assert "umeta" in _config.keys()