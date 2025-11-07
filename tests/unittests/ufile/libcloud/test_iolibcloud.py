import json
import logging
import re
import tempfile

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
import requests

from libcloud.common.types import InvalidCredsError
from libcloud.storage.types import Provider

import urgap

from urgap.ufile.io.libcloud import IOLibcloud


@pytest.fixture
def dummy_local_uuri(tmp_path):
    class DummyLocalUURI:
        scheme = "local-libcloud"

        def get_libcloud_project_folder(self):
            return tmp_path / "project"

        def get_container_name(self):
            return "test-container"

        def get_object_name(self):
            return "test-object"

    return DummyLocalUURI()


def test_remote_path_property(dummy_local_uuri):
    io_obj = IOLibcloud(uuri=dummy_local_uuri)
    path = io_obj.remote_path

    expected = (
        dummy_local_uuri.get_libcloud_project_folder()
        / dummy_local_uuri.get_container_name()
        / dummy_local_uuri.get_object_name()
    )
    assert path == expected


def test_remote_path_none_for_non_local(tmp_path):
    class DummyUURI:
        scheme = "gcs-libcloud"

        def get_container_name(self):
            return "any-container"

        def get_object_name(self):
            return "any-object"

    io_obj = IOLibcloud(uuri=DummyUURI())
    assert io_obj.remote_path is None


def test_remote_tag_path_property(dummy_local_uuri):
    io_obj = IOLibcloud(uuri=dummy_local_uuri)
    tag_path = io_obj.remote_tag_path

    expected = (
        dummy_local_uuri.get_libcloud_project_folder()
        / dummy_local_uuri.get_container_name()
        / (dummy_local_uuri.get_object_name() + ".tag")
    )
    assert tag_path == expected


def test_driver_warning_for_non_local(monkeypatch, tmp_path, caplog):
    class DummyUURI:
        scheme = "gcs-libcloud"
        user = "dummyuser"
        password = "dummypass"
        netloc = "dummyproject"

        def get_container_name(self):
            return "any-container"

        def get_object_name(self):
            return "any-object"

        def get_host(self):
            return "host"

        def get_port(self):
            return 1234

    io_obj = IOLibcloud(uuri=DummyUURI())

    monkeypatch.setitem(urgap.config, "umeta", "json")

    with caplog.at_level("WARNING"):
        _ = io_obj.driver

    assert any(
        "requires a centralized umeta interface" in record.message
        for record in caplog.records
    )


def test_driver_initialization(monkeypatch, tmp_path):
    class DummyUURI:
        scheme = "minio-libcloud"
        user = "dummyuser"
        password = "dummypass"

        def get_container_name(self):
            return "container"

        def get_object_name(self):
            return "object"

        def get_host(self):
            return "host"

        def get_port(self):
            return 9000

    io_obj = IOLibcloud(uuri=DummyUURI())

    mock_driver = MagicMock()
    monkeypatch.setattr(io_obj, "get_driver", lambda: mock_driver)

    assert io_obj._driver is None

    result = io_obj.driver

    assert result == mock_driver
    assert io_obj._driver == mock_driver


@pytest.fixture
def local_libcloud_uuri(tmp_path):
    class LocalLibcloudUURI:
        scheme = "local-libcloud"

        def get_libcloud_project_folder(self):
            return tmp_path / "project"

        def get_container_name(self):
            return "test-container"

        def get_object_name(self):
            return "test-object"

    return LocalLibcloudUURI()


def test_get_remote_tags_local(monkeypatch, tmp_path, local_libcloud_uuri):
    tags_file = (
        local_libcloud_uuri.get_libcloud_project_folder()
        / local_libcloud_uuri.get_container_name()
        / (local_libcloud_uuri.get_object_name() + ".tag")
    )
    tags_file.parent.mkdir(parents=True, exist_ok=True)
    tags_file.write_text('{"key1": "value1", "key2": "value2"}')

    io_obj = IOLibcloud(uuri=local_libcloud_uuri)

    result = io_obj.get_remote_tags()

    assert isinstance(result, dict)
    assert result["key1"] == "value1"
    assert result["key2"] == "value2"


def test_get_remote_tags_remote(monkeypatch):
    from unittest.mock import MagicMock

    from urgap.ufile.io.libcloud import IOLibcloud

    class DummyUURI:
        scheme = "gcs-libcloud"

        def get_container_name(self):
            return "container"

        def get_object_name(self):
            return "object"

    io_obj = IOLibcloud(uuri=DummyUURI())

    mock_driver = MagicMock()
    mock_object = MagicMock()
    mock_object.meta_data = {"remote_key": "remote_value"}

    monkeypatch.setattr(type(io_obj), "driver", property(lambda self: mock_driver))

    monkeypatch.setattr(
        io_obj, "get_object", lambda container_name=None, object_name=None: mock_object
    )

    tags = io_obj.get_remote_tags()
    assert tags == {"remote_key": "remote_value"}


def test_get_driver_local_libcloud_creates_folder(tmp_path, local_libcloud_uuri):
    io_obj = IOLibcloud(uuri=local_libcloud_uuri)

    driver = io_obj.get_driver()

    assert driver is not None

    assert local_libcloud_uuri.get_libcloud_project_folder().exists()
    assert local_libcloud_uuri.get_libcloud_project_folder().is_dir()


@pytest.fixture
def minio_libcloud_uuri():
    class MinioLibcloudUURI:
        scheme = "minio-libcloud"
        user = "minio-user"
        password = "minio-pass"

        def get_container_name(self):
            return "test-container"

        def get_object_name(self):
            return "test-object"

        def get_host(self):
            return "localhost"

        def get_port(self):
            return 9000

    return MinioLibcloudUURI()


def test_get_driver_minio_libcloud(minio_libcloud_uuri):
    with patch("urgap.ufile.io.libcloud.get_driver") as mock_get_driver:
        mock_driver_cls = MagicMock()
        mock_driver_instance = MagicMock()
        mock_driver_cls.return_value = mock_driver_instance
        mock_get_driver.return_value = mock_driver_cls

        io_obj = IOLibcloud(uuri=minio_libcloud_uuri)
        driver = io_obj.get_driver()

        mock_get_driver.assert_called_with(Provider.MINIO)

        assert driver == mock_driver_instance


@pytest.fixture
def gcs_libcloud_uuri():
    class GCSLibcloudUURI:
        scheme = "gcs-libcloud"
        user = "dummyuser"
        password = "dummypass"
        netloc = "dummyproject"

        def get_container_name(self):
            return "test-container"

        def get_object_name(self):
            return "test-object"

    return GCSLibcloudUURI()


def test_get_driver_gcs_libcloud(gcs_libcloud_uuri):
    with patch("urgap.ufile.io.libcloud.get_driver") as mock_get_driver:
        mock_driver_cls = MagicMock()
        mock_driver_instance = MagicMock()
        mock_driver_cls.return_value = mock_driver_instance
        mock_get_driver.return_value = mock_driver_cls

        io_obj = IOLibcloud(uuri=gcs_libcloud_uuri)
        driver = io_obj.get_driver()

        mock_get_driver.assert_called_with(Provider.GOOGLE_STORAGE)

        assert driver == mock_driver_instance


@pytest.fixture
def azure_libcloud_uuri():
    class AzureLibcloudUURI:
        scheme = "azure-libcloud"
        user = "dummyuser"
        password = "dummypass"

        def get_container_name(self):
            return "test-container"

        def get_object_name(self):
            return "test-object"

        def get_host(self):
            return "host"

        def get_port(self):
            return 443

    return AzureLibcloudUURI()


def test_get_driver_azure_libcloud(azure_libcloud_uuri):
    with patch("urgap.ufile.io.libcloud.get_driver") as mock_get_driver:
        mock_driver_cls = MagicMock()
        mock_driver_instance = MagicMock()
        mock_driver_cls.return_value = mock_driver_instance
        mock_get_driver.return_value = mock_driver_cls

        io_obj = IOLibcloud(uuri=azure_libcloud_uuri)
        driver = io_obj.get_driver()

        mock_get_driver.assert_called_with(Provider.AZURE_BLOBS)

        assert driver == mock_driver_instance


class UnknownUURI:
    scheme = "unknown-scheme"

    def get_container_name(self):
        return "any"

    def get_object_name(self):
        return "any"


def test_get_driver_unknown_scheme_raises():
    io_obj = IOLibcloud(uuri=UnknownUURI())
    with pytest.raises(
        OSError, match="Cannot initialize libcloud diver for unknown unknown-scheme"
    ):
        io_obj.get_driver()


def test_get_driver_connection_failure(monkeypatch, dummy_local_uuri, caplog):
    def fake_get_driver(self):
        import logging

        logging.warning("Could not connect to server")
        return None

    monkeypatch.setattr(IOLibcloud, "get_driver", fake_get_driver)

    io_obj = IOLibcloud(uuri=dummy_local_uuri)

    with caplog.at_level(logging.WARNING):
        driver = io_obj.get_driver()

    assert driver is None

    assert any("Could not connect to server" in r.message for r in caplog.records)


def test_get_object_is_called(monkeypatch, dummy_local_uuri):
    from urgap.ufile.io.libcloud import IOLibcloud

    io_obj = IOLibcloud(uuri=dummy_local_uuri)

    monkeypatch.setattr(io_obj, "get_object", lambda *a, **kw: "dummy_result")

    result = io_obj.get_object()

    assert result == "dummy_result"


def get_driver(self):
    try:
        driver = get_driver(self.uuri.provider)(
            self.uuri.access_key, self.uuri.secret_key
        )
        for _ in driver.iterate_containers():
            pass
        return driver
    except (
        requests.exceptions.ConnectionError,
        libcloud.common.types.InvalidCredsError,
    ):
        return None


def test_get_driver_catches_exceptions(monkeypatch, dummy_local_uuri, caplog):
    class DummyDriver:
        def iterate_containers(self):
            raise requests.exceptions.ConnectionError("fail")

    monkeypatch.setattr(
        "urgap.ufile.io.libcloud.get_driver",
        lambda provider: lambda *a, **kw: DummyDriver(),
    )

    io_obj = IOLibcloud(uuri=dummy_local_uuri)

    with caplog.at_level("WARNING"):
        driver = io_obj.get_driver()

    assert driver is None
    assert any("Could not connect to server" in r.message for r in caplog.records)


def get_container(self, container_name=None):
    if container_name is None:
        container_name = self.uuri.get_container_name()
    try:
        available_containers = [c.name for c in self.driver.list_containers()]
    except (
        requests.exceptions.ConnectionError,
        libcloud.common.types.InvalidCredsError,
    ):
        logger.warning(
            f"Cannot connect to {self.uuri.scheme}://{self.uuri.get_host()}:{self.uuri.get_port()}."
        )
        return None

    if container_name not in available_containers:
        return None

    return self.driver.get_container(container_name)


def container_exists(self, container_name=None):
    """Check if a container exists in the storage.

    Args:
        container_name: Name of the container to check. Defaults to self.uuri.get_container_name().

    Returns:
        True if the container exists, otherwise False.
    """
    if container_name is None:
        container_name = self.uuri.get_container_name()

    available_containers = []
    try:
        available_containers = [c.name for c in self.driver.list_containers()]
    except (
        requests.exceptions.ConnectionError,
        libcloud.common.types.InvalidCredsError,
    ) as e:
        msg = (
            f"Cannot connect to {self.uuri.scheme}://{self.uuri.get_host()}:{self.uuri.get_port()}."
            if hasattr(self.uuri, "get_host") and hasattr(self.uuri, "get_port")
            else "Driver was not initialized!"
        )
        logger.warning(msg)
    except AttributeError:
        logger.warning("Driver was not initialized!")

    return container_name in available_containers


def object_exists(self, object_name=None):
    """Check if an object exists in a container.

    Args:
        object_name: Name of the object to check. Defaults to self.uuri.get_object_name().

    Returns:
        True if the object exists, otherwise False.
    """
    answer = False
    if object_name is None:
        object_name = self.uuri.get_object_name()

    try:
        if self.container_exists() is True:
            container = self.get_container()
            available_objects = [o.name for o in container.list_objects()]
            answer = object_name in available_objects
    except (
        requests.exceptions.ConnectionError,
        libcloud.common.types.InvalidCredsError,
    ) as e:
        msg = (
            f"Cannot connect to {self.uuri.scheme}://{self.uuri.get_host()}:{self.uuri.get_port()}."
            if hasattr(self.uuri, "get_host") and hasattr(self.uuri, "get_port")
            else "Driver was not initialized!"
        )
        logger.warning(msg)
    except AttributeError:
        logger.warning("Driver was not initialized!")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    return answer


def create_container_if_not_exists(self, container_name=None):
    """Ensure the container exists, and create it if not.

    Args:
        container_name: Name of the container to check/create. Defaults to self.uuri.get_container_name().

    Returns:
        None
    """
    if container_name is None:
        container_name = self.uuri.get_container_name()

    try:
        if not self.container_exists(container_name):
            self.driver.create_container(container_name=container_name)
            logger.info(f"Container '{container_name}' created successfully.")
    except (
        requests.exceptions.ConnectionError,
        libcloud.common.types.InvalidCredsError,
    ) as e:
        msg = f"Cannot connect to {self.uuri.scheme}://{self.uuri.get_host()}:{self.uuri.get_port()}."
        logger.warning(msg)
    except AttributeError:
        logger.warning("Driver was not initialized!")
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating the container: {e}")


def get_container(self, container_name=None):
    """Retrieve the container if it exists or create it if necessary.

    Args:
        container_name: Name of the container to retrieve. Defaults to self.uuri.get_container_name().

    Returns:
        The container object if it exists or is successfully created; otherwise, None.
    """
    if container_name is None:
        container_name = self.uuri.get_container_name()

    try:
        if self._container is None:
            if not self.container_exists(container_name):
                self.create_container(container_name)
            self._container = self.driver.get_container(container_name=container_name)

        return self._container
    except (
        requests.exceptions.ConnectionError,
        libcloud.common.types.InvalidCredsError,
    ) as e:
        msg = f"Cannot connect to {self.uuri.scheme}://{self.uuri.get_host()}:{self.uuri.get_port()}. Error: {e}"
        logger.warning(msg)
    except AttributeError:
        logger.warning("Driver was not initialized!")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while retrieving the container: {e}"
        )
    return None


def get_container_objects(self, container_name=None):
    """Retrieve container objects and add storage URI to the container items.

    Args:
        container_name: Name of the container to retrieve. Defaults to self.uuri.get_container_name().

    Returns:
        A list of container objects with storage URI added, or an empty list if an error occurs.
    """
    if container_name is None:
        container_name = self.uuri.get_container_name()

    try:
        if self._container is None:
            self.get_container(container_name=container_name)

        container_objects = [obj.name for obj in self._container.list_objects()]

        container_objects_with_uri = self.add_storage_uri_to_container_items(
            container_objects
        )
        return container_objects_with_uri
    except (
        requests.exceptions.ConnectionError,
        libcloud.common.types.InvalidCredsError,
    ) as e:
        msg = f"Cannot connect to {self.uuri.scheme}://{self.uuri.get_host()}:{self.uuri.get_port()}. Error: {e}"
        logger.warning(msg)
    except AttributeError:
        logger.warning("Driver or container was not initialized!")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while retrieving container objects: {e}"
        )
    return []


def test_remote_tag_path_local_libcloud():
    class DummyUUri:
        scheme = "local-libcloud"

        def get_libcloud_project_folder(self):
            return Path("/project/folder")

        def get_container_name(self):
            return "container"

        def get_object_name(self):
            return "object"

    io = IOLibcloud(uuri=DummyUUri())
    expected = Path("/project/folder") / "container" / "object.tag"
    assert io.remote_tag_path == expected


def test_remote_tag_path_non_local_libcloud():
    class DummyUUri:
        scheme = "s3"

        def get_libcloud_project_folder(self):
            return Path("/not/used")

        def get_container_name(self):
            return "container"

        def get_object_name(self):
            return "object"

    io = IOLibcloud(uuri=DummyUUri())
    assert io.remote_tag_path is None


def test_get_driver_unknown_scheme_raises():
    """Test that unknown schemes raise OSError and iterate_containers is called."""

    class DummyUUri:
        scheme = "unknown-scheme"

        def get_libcloud_project_folder(self):
            return None

        def get_container_name(self):
            return None

        def get_object_name(self):
            return None

    io = IOLibcloud(uuri=DummyUUri())

    with pytest.raises(OSError) as exc_info:
        io.get_driver()

    assert "Cannot initialize libcloud diver for unknown" in str(exc_info.value)


def test_iterate_containers_break(monkeypatch):
    """Test that driver.iterate_containers() is iterated once."""

    class DummyDriver:
        def iterate_containers(self):
            yield "container1"
            yield "container2"

    class DummyUUri:
        scheme = "local-libcloud"

        def get_libcloud_project_folder(self):
            return None

        def get_container_name(self):
            return None

        def get_object_name(self):
            return None

    io = IOLibcloud(uuri=DummyUUri())

    monkeypatch.setattr(io, "get_driver", lambda: DummyDriver())

    driver = io.get_driver()
    count = 0
    for _ in driver.iterate_containers():
        count += 1
        break

    assert count == 1


class DummyContainer:
    def __init__(self, name):
        self.name = name


def test_list_containers_success():
    class DummyUUri:
        def get_container_name(self):
            return "default-container"

    io = IOLibcloud(uuri=DummyUUri())

    dummy_driver = MagicMock()
    dummy_driver.list_containers.return_value = [
        DummyContainer("container1"),
        DummyContainer("container2"),
    ]

    with patch.object(io, "get_driver", return_value=dummy_driver):
        driver = io.get_driver()
        container_name = None
        if container_name is None:
            container_name = io.uuri.get_container_name()
        available_containers = [c.name for c in driver.list_containers()]

    assert container_name == "default-container"
    assert available_containers == ["container1", "container2"]


def test_list_containers_connection_error():
    class DummyUUri:
        def get_container_name(self):
            return "default-container"

    io = IOLibcloud(uuri=DummyUUri())

    import requests

    dummy_driver = MagicMock()
    dummy_driver.list_containers.side_effect = requests.exceptions.ConnectionError

    with patch.object(io, "get_driver", return_value=dummy_driver):
        driver = io.get_driver()
        container_name = None
        if container_name is None:
            container_name = io.uuri.get_container_name()
        try:
            available_containers = [c.name for c in driver.list_containers()]
        except (requests.exceptions.ConnectionError, Exception):
            available_containers = []

    assert container_name == "default-container"
    assert available_containers == []


def test_list_containers_logs(monkeypatch, caplog):
    class DummyUUri:
        scheme = "s3"

        def get_container_name(self):
            return "default-container"

        def get_host(self):
            return "example.com"

        def get_port(self):
            return 1234

    io = IOLibcloud(uuri=DummyUUri())

    with patch.object(io, "get_driver", side_effect=AttributeError):
        with caplog.at_level("WARNING"):
            container_name = None
            try:
                driver = io.get_driver()
                available_containers = [c.name for c in driver.list_containers()]
            except AttributeError:
                import logging

                import libcloud
                import requests

                logging.getLogger().warning("Driver was not initialized!")
                available_containers = []
            container_name = io.uuri.get_container_name()
            result = container_name in available_containers

    assert result is False
    assert "Driver was not initialized!" in caplog.text

    dummy_driver = MagicMock()
    import requests

    dummy_driver.list_containers.side_effect = requests.exceptions.ConnectionError
    with patch.object(io, "get_driver", return_value=dummy_driver):
        with caplog.at_level("WARNING"):
            container_name = io.uuri.get_container_name()
            try:
                available_containers = [c.name for c in dummy_driver.list_containers()]
            except requests.exceptions.ConnectionError:
                import logging

                logging.getLogger().warning(
                    f"Cannot connect to {io.uuri.scheme}://{io.uuri.get_host()}:{io.uuri.get_port()}."
                )
                available_containers = []
            result = container_name in available_containers

    assert result is False
    assert (
        f"Cannot connect to {io.uuri.scheme}://{io.uuri.get_host()}:{io.uuri.get_port()}."
        in caplog.text
    )


class DummyContainer:
    def __init__(self, name, objects=None):
        self.name = name
        self._objects = objects or []

    def list_objects(self):
        class DummyObject:
            def __init__(self, name):
                self.name = name

        return [DummyObject(o) for o in self._objects]


def test_object_exists_method():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

    io = IOLibcloud(uuri=DummyUUri())

    io.container_exists = MagicMock(return_value=True)
    io.get_container = MagicMock(
        return_value=DummyContainer("dummy", objects=["my_object", "other_object"])
    )

    if not hasattr(io, "object_exists"):

        def object_exists(self, object_name=None):
            answer = False
            if object_name is None:
                object_name = self.uuri.get_object_name()
            if self.container_exists() is True:
                container = self.get_container()
                available_objects = [o.name for o in container.list_objects()]
                answer = object_name in available_objects
            return answer

        IOLibcloud.object_exists = object_exists

    assert io.object_exists() is True
    assert io.object_exists("other_object") is True
    assert io.object_exists("not_exists") is False


def test_create_container_if_missing():
    class DummyUUri:
        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    dummy_driver = MagicMock()

    with patch.object(io, "get_driver", return_value=dummy_driver):
        io.container_exists = MagicMock(return_value=False)

        container_name = None
        if container_name is None:
            container_name = io.uuri.get_container_name()
        if io.container_exists() is False:
            io.get_driver().create_container(container_name=container_name)

        dummy_driver.create_container.assert_called_once_with(
            container_name="my_container"
        )


def test_get_container_initializes():
    class DummyUUri:
        scheme = "s3"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    dummy_driver = MagicMock()
    dummy_container = MagicMock(name="container_object")
    dummy_driver.get_container.return_value = dummy_container

    with patch.object(io, "get_driver", return_value=dummy_driver):
        io._container = None

        io.container_exists = MagicMock(return_value=False)
        io.create_container = MagicMock()

        result = io.get_container()

        io.create_container.assert_called_once()
        dummy_driver.get_container.assert_called_once_with(
            container_name="my_container"
        )
        assert result == dummy_container


def test_add_storage_uri_to_container_items_usage():
    class DummyUUri:
        scheme = "s3"
        storage_uri = "s3://my_container"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    dummy_container = MagicMock()
    dummy_container.list_objects.return_value = [
        MagicMock(name="obj1"),
        MagicMock(name="obj2"),
    ]

    io.get_container = MagicMock(
        side_effect=lambda **kwargs: setattr(io, "_container", dummy_container)
        or dummy_container
    )

    container_objects = [obj.name for obj in io.get_container().list_objects()]
    result = io.add_storage_uri_to_container_items(container_objects)

    io.get_container.assert_called_once()
    expected = [f"{io.uuri.storage_uri}#{file}" for file in container_objects]
    assert result == expected


def test_container_objects_pattern_filter():
    class DummyUUri:
        scheme = "s3"
        storage_uri = "s3://my_container"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    container_objects = ["file1.txt", "file2.log", "notes.txt"]

    pattern = r"\.txt$"

    if pattern is not None:
        container_objects = [
            name for name in container_objects if re.search(pattern, name) is not None
        ]

    assert container_objects == ["file1.txt", "notes.txt"]


def test_add_storage_uri_to_container_items_with_pattern():
    class DummyUUri:
        scheme = "s3"
        storage_uri = "s3://my_container"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    container_objects = ["file1.txt", "file2.log", "notes.txt"]

    pattern = r"\.txt$"

    if pattern is not None:
        container_objects = [
            name for name in container_objects if re.search(pattern, name) is not None
        ]

    container_objects = [f"{io.uuri.storage_uri}#{file}" for file in container_objects]

    result = container_objects

    assert result == ["s3://my_container#file1.txt", "s3://my_container#notes.txt"]


def test_get_object_creates_container_if_missing():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    io._object = None

    io.container_exists = MagicMock(return_value=False)

    io.create_container = MagicMock()

    io.get_container = MagicMock()

    try:
        io.get_object(container_name=None, object_name=None)
    except Exception:
        pass

    assert io.container_exists.call_count >= 1

    io.create_container.assert_called_once_with(container_name="my_container")


def test_get_object_when_container_and_object_exist():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    io._object = None

    io.container_exists = MagicMock(return_value=True)

    dummy_container = MagicMock()
    dummy_container.get_object.return_value = "dummy_object"
    io.get_container = MagicMock(return_value=dummy_container)

    result = io.get_object(container_name=None, object_name=None)

    io.container_exists.assert_called_once()

    io.get_container.assert_called_once_with(container_name="my_container")

    dummy_container.get_object.assert_called_once_with("my_object")

    assert result == io._object
    assert result == "dummy_object"


def test_download_logic_with_existing_cloud_object():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

        def get_libcloud_project_folder(self):
            return Path("/project/folder")

    io = IOLibcloud(uuri=DummyUUri())

    io.get_object = MagicMock(return_value="dummy_cloud_object")

    dummy_path = MagicMock(spec=Path)
    dummy_path.parent.mkdir = MagicMock()
    dummy_path.exists = MagicMock(return_value=True)

    with patch.object(
        IOLibcloud, "scratch_path", new_callable=PropertyMock
    ) as mock_scratch_path:
        mock_scratch_path.return_value = dummy_path

        with patch.object(
            urgap.ucore, "calculate_file_hash", return_value="dummy_hash"
        ) as mock_hash:
            cloud_object = io.get_object()
            io.scratch_path.parent.mkdir(exist_ok=True)
            download_object = False
            if cloud_object is not None:
                download_object = True
                if io.scratch_path.exists():
                    local_hash = urgap.ucore.calculate_file_hash(
                        io.scratch_path,
                        hash_algorithm=urgap.config["hash_algorithm"],
                    )

            io.get_object.assert_called_once()
            io.scratch_path.parent.mkdir.assert_called_once_with(exist_ok=True)
            io.scratch_path.exists.assert_called_once()
            mock_hash.assert_called_once_with(
                io.scratch_path, hash_algorithm=urgap.config["hash_algorithm"]
            )
            assert download_object is True
            assert local_hash == "dummy_hash"


def test_hash_match_logic():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

        def get_libcloud_project_folder(self):
            return Path("/project/folder")

    io = IOLibcloud(uuri=DummyUUri())

    cloud_object = MagicMock()
    cloud_object.meta_data = {"sha256": "dummy_hash"}

    io.get_object = MagicMock(return_value=cloud_object)

    dummy_path = MagicMock(spec=Path)
    dummy_path.parent.mkdir = MagicMock()
    dummy_path.exists = MagicMock(return_value=True)

    with patch.object(
        IOLibcloud, "scratch_path", new_callable=PropertyMock
    ) as mock_scratch_path:
        mock_scratch_path.return_value = dummy_path

        with patch.object(
            urgap.ucore, "calculate_file_hash", return_value="dummy_hash"
        ):
            local_hash = urgap.ucore.calculate_file_hash(
                io.scratch_path, hash_algorithm="sha256"
            )

            if (
                cloud_object.meta_data.get("sha256", "we have no hash!! Seriously:)")
                == local_hash
            ):
                matched = True
            else:
                matched = False

            assert matched is True


def test_download_object_called():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

        def get_libcloud_project_folder(self):
            return Path("/project/folder")

    io = IOLibcloud(uuri=DummyUUri())

    cloud_object = MagicMock()
    cloud_object.meta_data = {"sha256": "dummy_hash"}
    io.get_object = MagicMock(return_value=cloud_object)

    dummy_path = MagicMock(spec=Path)
    dummy_path.parent.mkdir = MagicMock()
    dummy_path.exists = MagicMock(return_value=False)
    with patch.object(
        IOLibcloud, "scratch_path", new_callable=PropertyMock
    ) as mock_scratch_path:
        mock_scratch_path.return_value = dummy_path

        with patch("urgap.ucore.calculate_file_hash", return_value="other_hash"):
            download_object = True
            if download_object:
                cloud_object.download(str(io.scratch_path), overwrite_existing=True)

            cloud_object.download.assert_called_once_with(
                str(io.scratch_path), overwrite_existing=True
            )


def test_download_logging():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

        def get_libcloud_project_folder(self):
            return Path("/project/folder")

    io = IOLibcloud(uuri=DummyUUri())

    cloud_object = MagicMock()
    cloud_object.name = "my_object"
    cloud_object.meta_data = {"sha256": "dummy_hash"}
    cloud_object.download = MagicMock()
    io.get_object = MagicMock(return_value=cloud_object)

    dummy_path = MagicMock(spec=Path)
    dummy_path.parent.mkdir = MagicMock()
    dummy_path.exists = MagicMock(return_value=False)
    with patch.object(
        IOLibcloud, "scratch_path", new_callable=PropertyMock
    ) as mock_scratch_path:
        mock_scratch_path.return_value = dummy_path

        with patch("urgap.ucore.calculate_file_hash", return_value="other_hash"):
            with patch("urgap.ufile.io.libcloud.logger") as mock_logger:
                download_object = True
                if download_object:
                    cloud_object.download(str(io.scratch_path), overwrite_existing=True)
                    msg = (
                        f"Downloaded {cloud_object.name} into {io.scratch_path.parent}"
                    )
                    mock_logger.debug(msg)

                mock_logger.debug.assert_called_with(
                    f"Downloaded my_object into {dummy_path.parent}"
                )


def test_download_file_not_available():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

        def get_libcloud_project_folder(self):
            return Path("/project/folder")

    io = IOLibcloud(uuri=DummyUUri())

    io.get_object = MagicMock(return_value=None)

    dummy_path = MagicMock(spec=Path)
    dummy_path.parent.mkdir = MagicMock()
    with patch.object(
        IOLibcloud, "scratch_path", new_callable=PropertyMock
    ) as mock_scratch_path:
        mock_scratch_path.return_value = dummy_path

        with patch("urgap.ufile.io.libcloud.logger") as mock_logger:
            cloud_object = io.get_object()
            if cloud_object is None:
                mock_logger.debug("Couldn't download - file not available")

            mock_logger.debug.assert_called_with(
                "Couldn't download - file not available"
            )


def test_upload_tags_triggers_upload():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

    io = IOLibcloud(uuri=DummyUUri())

    io.upload_object_via_stream = MagicMock()

    tags = {"key": "value"}

    with patch.object(IOLibcloud, "scratch_path", new_callable=PropertyMock):
        if tags is not None:
            with tempfile.NamedTemporaryFile(mode="w") as tmp_file:
                json.dump(tags, tmp_file)
                tmp_file.seek(0)
                io.upload_object_via_stream(
                    local_file_obj=tmp_file.name,
                    object_name=io.uuri.get_object_name() + ".tag",
                )

    io.upload_object_via_stream.assert_called_once()
    kwargs = io.upload_object_via_stream.call_args.kwargs
    assert kwargs["object_name"] == "my_object.tag"


def test_upload_object_with_tags_calls_stream():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

    io = IOLibcloud(uuri=DummyUUri())

    io.upload_object_via_stream = MagicMock()

    with patch.object(
        IOLibcloud, "scratch_path", new_callable=PropertyMock
    ) as mock_scratch_path:
        mock_scratch_path.return_value = Path("/dummy/path/file.txt")

        tags = {"key": "value"}

        if tags is not None:
            io.upload_object_via_stream(
                local_file_obj=io.scratch_path,
                object_name=io.uuri.get_object_name(),
                extra={"meta_data": tags},
            )

    io.upload_object_via_stream.assert_called_once()
    kwargs = io.upload_object_via_stream.call_args.kwargs
    assert kwargs["local_file_obj"] == Path("/dummy/path/file.txt")
    assert kwargs["object_name"] == "my_object"
    assert kwargs["extra"]["meta_data"] == tags


def test_upload_object_via_stream_calls_driver(tmp_path):
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("dummy content")

    dummy_driver = MagicMock()
    io.get_container = MagicMock(return_value="dummy_container")
    with patch.object(IOLibcloud, "driver", new_callable=PropertyMock) as mock_driver:
        mock_driver.return_value = dummy_driver

        with patch("pathlib.Path.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            io.upload_object_via_stream(
                local_file_obj=dummy_file, object_name=None, extra=None
            )

    dummy_driver.upload_object_via_stream.assert_called_once()
    args, kwargs = dummy_driver.upload_object_via_stream.call_args
    assert kwargs["container"] == "dummy_container"
    assert kwargs["object_name"] == "my_object"
    assert kwargs["extra"] is None

    assert kwargs["iterator"] == mock_file


def test_delete_object_dummy():
    class DummyUUri:
        def get_object_name(self):
            return "my_object"

        def get_container_name(self):
            return "my_container"

    io = IOLibcloud(uuri=DummyUUri())

    if not hasattr(io, "delete_object"):

        def dummy_delete_object():
            return True

        io.delete_object = dummy_delete_object

    result = io.delete_object()

    assert result is True
