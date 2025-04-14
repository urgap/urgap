import json
from pathlib import Path

import pytest
import requests



def test_setting_requests_timeouts(tmp_dir):
        json.dump(
            {
                "requests_timeout_connect": {"value": None},
                "requests_timeout_read": {"value": None},
            },
            fp,
            indent=4,
        )
    working_request = requests.get(
        "https://google.com",
        timeout=(
            _config["requests_timeout_connect"],
            _config["requests_timeout_read"],
        ),
    )
    assert working_request.status_code == 200

        json.dump(
            {
                "requests_timeout_connect": {"value": 1e-6},
                "requests_timeout_read": {"value": 1e-6},
            },
            fp,
            indent=4,
        )
    with pytest.raises(Exception):
            "https://google.com",
            timeout=(
                _config["requests_timeout_connect"],
                _config["requests_timeout_read"],
            ),
        )