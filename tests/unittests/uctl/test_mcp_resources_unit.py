import types
import urllib.parse

import pytest

from fastmcp import Client, FastMCP

import urgap

from urgap.uctl.mcp.resources import register_resources


@pytest.fixture
def resource_client():
    """Provide an in-memory client connected to a server with the urgap resources."""
    server = FastMCP("urgap resources test server")
    register_resources(server)
    return Client(server)


async def _read_text(client, uri):
    """Read a resource and return its text content."""
    contents = await client.read_resource(uri)
    assert contents, f"No content returned for {uri}"
    return contents[0].text


@pytest.mark.asyncio
async def test_register_resources_registers_all(resource_client):
    async with resource_client as client:
        templates = {
            template.uri_template: template
            for template in await client.list_resource_templates()
        }

    assert set(templates) == {
        "uu-greeting://{name}",
        "mylabdata-uat://{equipment_id}/{task_id}/{data_type}/{path}",
        "mylabdata-uat-storage-base://{equipment_id}/{task_id}",
        "gcp-storage-base://{project_id}/{bucket}",
    }
    assert templates["uu-greeting://{name}"].name == "Personal Greeting"
    assert templates["uu-greeting://{name}"].mime_type == "text/plain"


@pytest.mark.asyncio
async def test_register_resources_and_call(resource_client, monkeypatch):
    monkeypatch.setattr(
        urgap.instances,
        "utree_querier",
        types.SimpleNamespace(get_nodes_with_ext=lambda ext: ["any.ANY", "other.TYPE"]),
    )

    async with resource_client as client:
        assert await _read_text(client, "uu-greeting://Abc") == "Hello there Abc"

        quoted = urllib.parse.quote("folder/with/slash.txt", safe="")
        out = await _read_text(client, f"mylabdata-uat://354557/24-1-C4/txt/{quoted}")
        assert out == (
            "mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-1-C4"
            "?uftype=any.ANY#folder/with/slash.txt"
        )

        base = await _read_text(client, "mylabdata-uat-storage-base://354557/24-1-C4")
        assert base == "mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-1-C4"


@pytest.mark.asyncio
async def test_generate_gcp_storage_base(resource_client):
    async with resource_client as client:
        result = await _read_text(client, "gcp-storage-base://my-project/my-bucket")

    assert result == "gcs://my-project/my-bucket"
