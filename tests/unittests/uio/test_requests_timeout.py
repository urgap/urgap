from pathlib import Path

import pytest



def test_setting_requests_timeouts(tmp_dir):
    working_request = requests.get(
        "https://google.com",
    )
    assert working_request.status_code == 200

    with pytest.raises(Exception):
            "https://google.com",
        )