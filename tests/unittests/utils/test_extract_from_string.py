

def test_extract_from_string_one_match():
        any_string="One Ring to rule them all.",
        regex_pattern=r"One Ring",
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
        any_string="One Ring to find them.",
        regex_pattern=r"to rule them all",
    )
    assert len(match) == 0
    assert isinstance(match, list)