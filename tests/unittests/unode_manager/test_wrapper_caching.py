

def test_uimporter_import_wrappers():
    assert (
        is not None
    )


def test_uimporter_import_unodes():
    """Test if new u3 structure of imports work using example BasicFunctionTestNode."""
    for expected_version in ["1.1.0", "1.3.0", "latest"]:
        assert (
                f"BasicFunctionTestNode:{expected_version}",
                None,
            )
            is not None
        )


def test_init_unode_fails(caplog):
    assert "UNode not_a_unode not available." in caplog.text