import pytest

from urgap.umeta.io.postgresql import UMeta


def test_umeta_init():
    # Instantiate the UMeta class
    umeta = UMeta()

    # Check that the base attributes are initialized correctly
    assert umeta._db is None
    assert umeta._session is None
    assert umeta.name == "UMeta postgresql"


def test_generate_connection_string(monkeypatch):
    # Provide a dummy config dictionary
    dummy_config = {"umeta-postgresql-url": "postgresql://dummyhost:5432"}

    # Patch urgap.config to use the dummy dictionary
    monkeypatch.setattr("urgap.config", dummy_config)

    # Patch extract_credentials to return dummy credentials
    monkeypatch.setattr(
        "urgap.instances.ucredential_manager.extract_credentials",
        lambda uri: {"user": "dummyuser", "password": "dummypass"},
    )

    umeta = UMeta()
    conn_str = umeta.generate_connection_string()

    # Expected string should include dummy credentials
    expected = "postgresql://dummyuser:dummypass@dummyhost:5432"
    assert conn_str == expected


def test_generate_connection_string_credentials(monkeypatch):
    # Mock the config to provide a dummy PostgreSQL URI
    monkeypatch.setattr(
        "urgap.config", {"umeta-postgresql-url": "postgresql://localhost:5432"}
    )

    # Mock the credential extraction to return fixed credentials
    monkeypatch.setattr(
        "urgap.instances.ucredential_manager.extract_credentials",
        lambda uri: {"user": "testuser", "password": "testpass"},
    )

    umeta = UMeta()
    conn_str = umeta.generate_connection_string()

    expected = "postgresql://testuser:testpass@localhost:5432"
    assert conn_str == expected
