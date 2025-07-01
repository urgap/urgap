import pytest

import urgap


def test_set_umeta_fails_module_not_found_error():
    with pytest.raises(ModuleNotFoundError):
        um = urgap.UMeta(io="Mitsurugi")
        um.io