import logging
import os

import google.api_core.exceptions
import google_crc32c
import pytest

import urgap

from urgap.ucredentials.io._base import IOBaseCreds
from urgap.ucredentials.io.gcp import IOGCPCreds


def test_reading_basic_json(tmp_scratch_disk):
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"
    us = urgap.UCredentialManager(json_path=c_json)
    assert len(us.ingested_credentials) == 2


def test_reading_basic_json_writing(tmp_scratch_disk):
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"
    o_json = tmp_scratch_disk / "tmp.json"
    us = urgap.UCredentialManager(json_path=c_json)
    us.write_credentials(json_path=o_json)

    us2 = urgap.UCredentialManager(json_path=o_json)
    o_json.unlink()

    assert len(us.ingested_credentials) == len(us2.ingested_credentials)


def test_crash(tmp_scratch_disk):
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"
    o_json = tmp_scratch_disk / "tmp.json"
    us = urgap.UCredentialManager(json_path=c_json)
    us.write_credentials(json_path=o_json)

    with pytest.raises(KeyError):
        us.extract_credentials("whatshappening")


def test_adding_new_lookup_json_works(tmp_scratch_disk):
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"

    o_json = tmp_scratch_disk / "tmp.json"

    cred_manager = urgap.UCredentialManager(json_path=c_json)

    new_cred = [
        {
            "description": "Demo1",
            "scheme": "smb",
            "host": "localhost:9000",
            "base_url": "smb://localhost:9000",
            "user": "LOCAL_USER",
            "password": "LOCAL_PASSWORD",
            "secure": True,
            "secret_store": "env",
        },
    ]
    cred_manager.add_credentials(new_cred)

    cred_manager.write_credentials(json_path=o_json)

    cred_manager2 = urgap.UCredentialManager(json_path=o_json)

    o_json.unlink(missing_ok=True)

    assert len(cred_manager2.ingested_credentials) == len(
        cred_manager.ingested_credentials,
    )


def test_adding_duplicate_is_overwriting_old(tmp_scratch_disk):
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"

    standard_lookup = [
        {
            "description": "Demo1",
            "scheme": "smb",
            "host": "localhost:9000",
            "base_url": "smb://localhost:9000",
            "user": "LOCAL_USER",
            "password": "LOCAL_PASSWORD",
            "secure": True,
            "secret_store": "env",
        },
    ]

    os.environ["LOCAL_USER"] = "Mitsurugi"
    os.environ["LOCAL_PASSWORD"] = "+==|----->"

    us = urgap.UCredentialManager(json_path=c_json)
    us.add_credentials(standard_lookup)

    key = standard_lookup[0]["base_url"]

    assert us.get_user(key) == "Mitsurugi"
    initial_count = len(us.ingested_credentials)
    assert initial_count >= 1

    os.environ["LOCAL_USER"] = "Horst"
    os.environ["LOCAL_PASSWORD"] = "Walter"

    us.add_credentials(standard_lookup)

    assert us.get_user(key) == "Horst"
    assert len(us.ingested_credentials) == initial_count


def test_env_extraction_works(tmp_scratch_disk):
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"

    standard_lookup = [
        {
            "description": "Demo1",
            "scheme": "smb",
            "host": "localhost:9000",
            "base_url": "smb://localhost:9000",
            "user": "M_USER",
            "password": "M_PASSWORD",
            "secure": True,
            "secret_store": "env",
        },
    ]

    os.environ["M_USER"] = "Horst"
    os.environ["M_PASSWORD"] = "Walter"

    cred_manager = urgap.UCredentialManager(json_path=c_json)
    cred_manager.add_credentials(standard_lookup)

    assert cred_manager.get_user(standard_lookup[0]) == "Horst"
    assert cred_manager.get_password(standard_lookup[0]) == "Walter"
    del os.environ["M_USER"]
    del os.environ["M_PASSWORD"]

    cred_id = cred_manager.ID_KEY.format(**standard_lookup[0])
    assert cred_manager.get_user(cred_id) == "Horst"


def test_echo_init_works():
    us = urgap.UCredentialManager()
    us.init_io_class(secret_store="echo", secret_id="MITSURUGI")
    assert us.io.get_secret() == "MITSURUGI"

    us.init_io_class(secret_store="echo", secret_id="Precious")
    assert us.io.get_secret() == "Precious"


def test_env_init_works():
    os.environ["MITSURUGI"] = "rōnin"
    us = urgap.UCredentialManager()
    us.init_io_class(secret_store="env", secret_id="MITSURUGI")
    assert us.io.get_secret() == "rōnin"
    del os.environ["MITSURUGI"]


def test_missing_io_class_raises_importerror():
    us = urgap.UCredentialManager()
    with pytest.raises(ImportError) as e:
        us.init_io_class(secret_store="nonexistent_backend", secret_id="dummy")
    assert "cannot be imported due to missing dependencies" in str(e.value)


def test_registered_backend_with_bad_class_logs_and_raises(caplog, monkeypatch):
    """secret_store is registered but the class can't actually construct with
    the given kwargs -> generic instantiation raises TypeError, which
    init_io_class logs and re-raises.
    """
    us = urgap.UCredentialManager()

    monkeypatch.setitem(us.available_io_classes, "fake_backend", object)

    with pytest.raises(TypeError):
        us.init_io_class(secret_store="fake_backend", secret_id="dummy")

    assert "Could not initialize secret backend 'fake_backend'" in caplog.text


def test_new_backend_with_novel_kwarg_needs_no_manager_changes(monkeypatch):
    """A backend using a parameter name the manager has never seen (e.g. a
    GSK-only backend defined outside urgap-dev) still works, since
    init_io_class forwards **extra generically instead of enumerating
    known kwarg names.
    """

    class IOVaultCreds(IOBaseCreds):
        SCHEME = "vault_for_test"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.namespace = kwargs["namespace"]

        def get_secret(self):
            return f"{self.secret_id}@{self.namespace}"

    us = urgap.UCredentialManager()
    monkeypatch.setitem(us.available_io_classes, "vault_for_test", IOVaultCreds)

    us.init_io_class(secret_store="vault_for_test", secret_id="db-pw", namespace="team-ns")

    assert us.io.get_secret() == "db-pw@team-ns"


def test_get_user_warns_without_entry_or_key(caplog):
    ucm = urgap.UCredentialManager()

    with caplog.at_level("WARNING"):
        result = ucm.get_user(None)

    assert "Can only get user based on cred_entry or cred_key" in caplog.text
    assert result is None


def test_get_password_warns_without_entry_or_key(caplog):
    ucm = urgap.UCredentialManager()

    with caplog.at_level("WARNING"):
        result = ucm.get_password(None)

    assert "Can only get password based on cred_entry or cred_key" in caplog.text
    assert result is None


def test_null_user_works():
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"

    standard_lookup = [
        {
            "description": "Demo1",
            "scheme": "smb",
            "host": "localhost:9000",
            "base_url": "smb://localhost:9000",
            "user": None,
            "password": "M_PASSWORD",
            "secure": True,
            "secret_store": "env",
        },
    ]

    os.environ["M_PASSWORD"] = "Walter"

    cred_manager = urgap.UCredentialManager(json_path=c_json)
    cred_manager.add_credentials(standard_lookup)

    assert cred_manager.get_user(standard_lookup[0]) is None
    assert cred_manager.get_password(standard_lookup[0]) == "Walter"

    del os.environ["M_PASSWORD"]

    cred_id = cred_manager.ID_KEY.format(**standard_lookup[0])
    assert cred_manager.get_user(cred_id) is None


def test_io_base_creds_get_secret_raises():
    creds = IOBaseCreds(secret_id="dummy")
    with pytest.raises(NotImplementedError):
        creds.get_secret()


def test_concrete_subclass_without_get_secret_raises_when_called():
    class IOIncompleteCreds(IOBaseCreds):
        SCHEME = "incomplete_for_test"

    creds = IOIncompleteCreds(secret_id="dummy")
    with pytest.raises(NotImplementedError):
        creds.get_secret()


def test_concrete_subclass_without_scheme_raises_at_class_definition():
    with pytest.raises(TypeError) as excinfo:
        type("IONoSchemeCreds", (IOBaseCreds,), {"get_secret": lambda self: "unreachable"})

    assert "must define a non-empty SCHEME" in str(excinfo.value)


def test_abstract_intermediate_subclass_is_allowed():
    class _SharedCredsBase(IOBaseCreds, abstract=True):
        def get_secret(self) -> str:
            return "unreachable"

    assert getattr(_SharedCredsBase, "SCHEME", None) is None

    class IOConcreteCreds(_SharedCredsBase):
        SCHEME = "shared_for_test"

    inst = IOConcreteCreds(secret_id="dummy")
    assert inst.get_secret() == "unreachable"


def test_missing_secret_id_raises_typeerror():
    class IODummyCreds(IOBaseCreds):
        SCHEME = "dummy_for_test"

        def get_secret(self):
            return self.secret_id

    with pytest.raises(TypeError) as excinfo:
        IODummyCreds()
    assert "requires 'secret_id'" in str(excinfo.value)


def test_gcp_io_class_init(monkeypatch):
    """init_io_class forwards **extra generically; gcp.py now reads
    cloud_host_pid directly (renamed internally to self.project_id).
    """

    class DummyGCPClass:
        def __init__(self, secret_id, cloud_host_pid, version_id="latest"):
            self.secret_id = secret_id
            self.project_id = cloud_host_pid
            self.version_id = version_id

    us = urgap.UCredentialManager()
    monkeypatch.setitem(us.available_io_classes, "gcp", DummyGCPClass)

    us.init_io_class(
        secret_store="gcp",
        secret_id="dummy",
        cloud_host_pid="project123",
        version_id="latest",
    )

    assert isinstance(us.io, DummyGCPClass)
    assert us.io.secret_id == "dummy"
    assert us.io.project_id == "project123"
    assert us.io.version_id == "latest"


def test_akv_io_class_init(monkeypatch):
    class DummyAKV:
        def __init__(self, secret_id, cloud_host_pid):
            self.secret_id = secret_id
            self.vault_name = cloud_host_pid

    us = urgap.UCredentialManager()
    monkeypatch.setitem(us.available_io_classes, "akv", DummyAKV)

    us.init_io_class(secret_store="akv", secret_id="dummy", cloud_host_pid="vault123")

    assert us._io.secret_id == "dummy"
    assert us._io.vault_name == "vault123"


def test_ingest_cred_entry_invalid_logs_warning(monkeypatch, caplog):
    us = urgap.UCredentialManager()

    monkeypatch.setattr(us, "validate_credential_entry", lambda x: None)

    cred_entry = {
        "description": "DemoInvalid",
        "scheme": "invalid-scheme",
        "host": "localhost",
        "user": "USER",
        "password": "PASS",
        "secure": True,
        "secret_store": "env",
    }

    with caplog.at_level("WARNING"):
        us.ingest_cred_entry(cred_entry)

    assert (
        f"The credentials for {us.ID_KEY.format(**cred_entry)} were not valid"
        in caplog.text
    )


def test_read_credentials_warns_for_missing_file(tmp_path, caplog):
    us = urgap.UCredentialManager(json_path=None)
    fake_path = tmp_path / "non_existent.json"

    with caplog.at_level("WARNING"):
        try:
            us.read_credentials(json_path=fake_path)
        except KeyError:
            pass

    assert f"{fake_path} does not exist!" in caplog.text


def test_gcp_credential_with_explicit_pid(monkeypatch):
    """extract_credentials still honors an explicit cloud_host_pid;
    gcp.py now reads it directly (no manager-side aliasing needed).
    """
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"

    credential_with_pid = {
        "description": "GCP Demo",
        "scheme": "gcp-demo",
        "host": "localhost",
        "user": "G_USER",
        "password": "G_PASS",
        "secure": True,
        "secret_store": "gcp",
        "cloud_host_pid": "project123",
    }

    us = urgap.UCredentialManager(json_path=c_json)
    us.add_credentials([credential_with_pid])

    class DummyGCPClass:
        def __init__(self, secret_id, cloud_host_pid, version_id="latest", **kwargs):
            self.secret_id = secret_id
            self.project_id = cloud_host_pid
            self.version_id = version_id

        def get_secret(self):
            return self.secret_id

    monkeypatch.setitem(us.available_io_classes, "gcp", DummyGCPClass)

    secrets = us.extract_credentials("gcp-demo://localhost")

    assert secrets["user"] == "G_USER"
    assert secrets["password"] == "G_PASS"
    assert us.io.project_id == "project123"
    assert us.io.version_id == "latest"


def test_gcp_credential_falls_back_to_host(monkeypatch):
    """No explicit cloud_host_pid -> falls back to host, same as before
    this refactor.
    """
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"

    credential_no_pid = {
        "description": "GCP Demo No PID",
        "scheme": "gcp-demo-nopid",
        "host": "10.0.0.9",
        "user": "G_USER",
        "password": "G_PASS",
        "secure": True,
        "secret_store": "gcp",
    }

    us = urgap.UCredentialManager(json_path=c_json)
    us.add_credentials([credential_no_pid])

    class DummyGCPClass:
        def __init__(self, secret_id, cloud_host_pid, version_id="latest", **kwargs):
            self.secret_id = secret_id
            self.project_id = cloud_host_pid
            self.version_id = version_id

        def get_secret(self):
            return self.secret_id

    monkeypatch.setitem(us.available_io_classes, "gcp", DummyGCPClass)

    us.extract_credentials("gcp-demo-nopid://10.0.0.9")

    assert us.io.project_id == "10.0.0.9"


def test_non_gcp_akv_backend_honors_explicit_cloud_host_pid(monkeypatch):
    """A backend other than gcp/akv that sets cloud_host_pid explicitly in
    its JSON entry gets that value honored, not silently overridden by host.
    """
    c_json = urgap._test_folder / "data" / "configs" / "credentials_lookup.json"

    credential = {
        "description": "Vault Demo",
        "scheme": "vault-demo",
        "host": "unrelated-host",
        "user": "V_USER",
        "password": "V_PASS",
        "secure": True,
        "secret_store": "vault_for_test",
        "cloud_host_pid": "explicit-namespace",
    }

    us = urgap.UCredentialManager(json_path=c_json)
    us.add_credentials([credential])

    class IOVaultCreds(IOBaseCreds):
        SCHEME = "vault_for_test"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.cloud_host_pid = kwargs["cloud_host_pid"]

        def get_secret(self):
            return f"{self.secret_id}@{self.cloud_host_pid}"

    monkeypatch.setitem(us.available_io_classes, "vault_for_test", IOVaultCreds)

    secrets = us.extract_credentials("vault-demo://unrelated-host")

    assert secrets["user"] == "V_USER@explicit-namespace"


def test_get_secret_initialization(monkeypatch):
    class DummyPayload:
        def __init__(self, data: bytes):
            self.data = data

            crc = google_crc32c.Checksum()
            crc.update(data)
            self.data_crc32c = int(crc.hexdigest(), 16)

    class DummyResponse:
        def __init__(self):
            self.payload = DummyPayload(b"supersecret")

    class DummyClient:
        def access_secret_version(self, request):
            return DummyResponse()

    monkeypatch.setattr(
        "urgap.ucredentials.io.gcp.secretmanager.SecretManagerServiceClient",
        lambda: DummyClient(),
    )

    creds = IOGCPCreds(secret_id="dummy", cloud_host_pid="proj", version_id="1")
    result = creds.get_secret()

    assert result == "supersecret"


def test_get_secret_exception(monkeypatch, caplog):
    class DummyClient:
        def access_secret_version(self, request):
            raise google.api_core.exceptions.PermissionDenied("Access denied")

    monkeypatch.setattr(
        "urgap.ucredentials.io.gcp.secretmanager.SecretManagerServiceClient",
        lambda: DummyClient(),
    )

    creds = IOGCPCreds(secret_id="dummy", cloud_host_pid="proj", version_id="1")

    with caplog.at_level(logging.WARNING):
        result = creds.get_secret()

    assert "Secret could not be retrieved from GCP." in caplog.text
    assert result is None


def test_get_secret_crc32c(monkeypatch, caplog):
    class DummyPayloadMatch:
        def __init__(self, data: bytes):
            self.data = data
            crc = google_crc32c.Checksum()
            crc.update(data)
            self.data_crc32c = int(crc.hexdigest(), 16)

    class DummyResponseMatch:
        def __init__(self):
            self.payload = DummyPayloadMatch(b"secret_data")

    class DummyClientMatch:
        def access_secret_version(self, request):
            return DummyResponseMatch()

    monkeypatch.setattr(
        "urgap.ucredentials.io.gcp.secretmanager.SecretManagerServiceClient",
        lambda: DummyClientMatch(),
    )

    creds = IOGCPCreds(secret_id="dummy", cloud_host_pid="proj", version_id="1")
    secret = creds.get_secret()
    assert secret == "secret_data"

    class DummyPayloadCorrupt:
        def __init__(self, data: bytes):
            self.data = data
            self.data_crc32c = 0

    class DummyResponseCorrupt:
        def __init__(self):
            self.payload = DummyPayloadCorrupt(b"bad_secret")

    class DummyClientCorrupt:
        def access_secret_version(self, request):
            return DummyResponseCorrupt()

    monkeypatch.setattr(
        "urgap.ucredentials.io.gcp.secretmanager.SecretManagerServiceClient",
        lambda: DummyClientCorrupt(),
    )

    with caplog.at_level(logging.WARNING):
        secret = creds.get_secret()

    assert "Secret payload is corrupted (checksum mismatch)." in caplog.text
    assert secret == "bad_secret"


def test_null_user_and_stringify_json_password():
    us = urgap.UCredentialManager()
    us.add_credentials(
        [
            {
                "scheme": "gcs",
                "host": "test",
                "user": None,
                "password": '{"hello": "world", "cat": "dog"}',
                "secure": True,
                "description": "",
                "secret_store": "echo",
                "cloud_host_pid": "EMPTY",
            },
        ],
    )
    assert us.get_user("gcs://test") is None
    assert us.get_password("gcs://test") == '{"hello": "world", "cat": "dog"}'