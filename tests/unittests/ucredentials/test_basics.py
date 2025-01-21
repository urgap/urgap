import os

import pytest



def test_echo_init_works():
    us.init_io_class(secret_store="echo", secret_id="MITSURUGI")
    assert us.io.get_secret() == "MITSURUGI"

    us.init_io_class(secret_store="echo", secret_id="Precious")
    assert us.io.get_secret() == "Precious"


def test_env_init_works():
    os.environ["MITSURUGI"] = "rōnin"
    us.init_io_class(secret_store="env", secret_id="MITSURUGI")
    assert us.io.get_secret() == "rōnin"
    del os.environ["MITSURUGI"]