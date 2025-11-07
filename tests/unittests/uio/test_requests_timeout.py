import json

from pathlib import Path

import pytest
import requests

import urgap


def test_setting_requests_timeouts(tmp_dir):
    with open(Path(tmp_dir) / "urgap.json", "w") as fp:
        json.dump(
            {
                "requests_timeout_connect": {"value": None},
                "requests_timeout_read": {"value": None},
            },
            fp,
            indent=4,
        )
    _config = urgap.uinit.read_config(home_dir=tmp_dir)
    working_request = requests.get(
        "https://google.com",
        timeout=(
            _config["requests_timeout_connect"],
            _config["requests_timeout_read"],
        ),
    )
    assert working_request.status_code == 200

    with open(Path(tmp_dir) / "urgap.json", "w") as fp:
        json.dump(
            {
                "requests_timeout_connect": {"value": 1e-6},
                "requests_timeout_read": {"value": 1e-6},
            },
            fp,
            indent=4,
        )
    _config = urgap.uinit.read_config(home_dir=tmp_dir)
    with pytest.raises(Exception):
        requests.get(
            "https://google.com",
            timeout=(
                _config["requests_timeout_connect"],
                _config["requests_timeout_read"],
            ),
        )
