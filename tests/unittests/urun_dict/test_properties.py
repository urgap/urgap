import re


def test_init_creates_wid():
    assert urd_1.wid != urd_2.wid
    for urd in [urd_1, urd_2]:
        assert (
            bool(
                re.search(
                    urd.wid,
            )
            is True
        )