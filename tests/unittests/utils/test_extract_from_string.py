

def test_extract_from_string_one_match():
    )
    assert len(match) == 1
    assert match == ["One Ring"]


def test_extract_from_string_dates():
        any_string="The War of the Ring lasted from TA 3018 to TA 3019.",
        regex_pattern=r"TA \d{4}",
    )
    assert len(match) == 2
    assert "TA 3018" and "TA 3019" in match


def test_extract_from_string_no_match():
    )
    assert len(match) == 0
    assert isinstance(match, list)