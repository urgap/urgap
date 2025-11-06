import types
import urllib.parse

import urgap

from urgap.uctl.mcp.resources import register_resources


class DummyServer:
    def __init__(self):
        self.resources = {}

    def resource(self, pattern, name, description, mime_type):
        def decorator(fn):
            self.resources[name] = fn
            return fn

        return decorator


def test_register_resources_and_call(monkeypatch):
    monkeypatch.setattr(
        urgap.instances,
        "utree_querier",
        types.SimpleNamespace(get_nodes_with_ext=lambda ext: ["any.ANY", "other.TYPE"]),
    )

    srv = DummyServer()
    register_resources(srv)

    assert srv.resources["Personal Greeting"]("Abc") == "Hello there Abc"

    quoted = urllib.parse.quote("folder/with/slash.txt", safe="")
    out = srv.resources["urgap uri for a file in mylabdata uat"](
        equipment_id="354557",
        task_id="24-1-C4",
        data_type="txt",
        path=quoted,
    )
    assert (
        out
        == "mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-1-C4?uftype=any.ANY#folder/with/slash.txt"
    )

    base = srv.resources["urgap storage base for mylabdata uat"]("354557", "24-1-C4")
    assert base == "mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-1-C4"


def test_generate_gcp_storage_base():
    from urgap.uctl.mcp.resources import register_resources

    class DummyServer:
        def __init__(self):
            self.resources = {}

        def resource(self, pattern, name, description, mime_type):
            def decorator(fn):
                self.resources[name] = fn
                return fn

            return decorator

    srv = DummyServer()
    register_resources(srv)

    result = srv.resources["urgap storage base for google cloud"](
        "my-project", "my-bucket"
    )
    assert result == "gcs://my-project/my-bucket"