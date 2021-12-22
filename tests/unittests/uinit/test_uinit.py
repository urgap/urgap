import json

def test_create_home_folder(tmp_dir):


    assert (
        Path(
        ).exists()
        is True
    )


def test_copy_config_if_needed(tmp_dir):


def test_read_config(tmp_dir):
        json.dump({"umeta": {"value": "dummy"}}, fp, indent=4)
    assert "umeta" in _config.keys()