import pprint

import pytest

from mcp import ClientSession
from mcp.client.sse import sse_client


@pytest.mark.parametrize(
    "provide_uctl_server",
    [("FilterTabularToCSV:1.0.0", "CompressToTar:1.0.0", "VennDiagram:2.0.0", 41999)],
    indirect=["provide_uctl_server"],
)
@pytest.mark.asyncio
async def test_run_mcp(capfd, provide_uctl_server):
    await run()
    assert (
        "{'call': 'gcp_urgap_storage_pattern', 'result': 'gcs://some_gcp_bucket/folder/to/files'}"
        in capfd.readouterr().out
    )


async def run():
    server_url = "http://localhost:41999/sse"
    _streams_context = sse_client(url=server_url)
    streams = await _streams_context.__aenter__()

    _session_context = ClientSession(*streams)
    session: ClientSession = await _session_context.__aenter__()

    await session.initialize()

    print("Initialized SSE client...")
    print("Listing tools...")
    response = await session.list_tools()
    print("\nConnected to server with tools:")
    available_tools = [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema,
        }
        for tool in response.tools
    ]
    pprint.pprint(available_tools)

    result = await session.call_tool(
        "gcp_urgap_storage_pattern",
        {
            "project_id": "some_gcp_bucket",
            "bucket": "folder/to/files",
        },
    )
    print(
        {
            "call": "gcp_urgap_storage_pattern",
        }
    )

    await _session_context.__aexit__(None, None, None)
    await _streams_context.__aexit__(None, None, None)