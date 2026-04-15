import json
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession
import pytest
import httpx

import urgap

MCP_PORT = 41998


@pytest.mark.asyncio
@pytest.mark.parametrize("provide_mcp_tools_server", [MCP_PORT], indirect=True)
async def test_urgap_tools_mcp_server(provide_mcp_tools_server):
    url = f"http://localhost:{MCP_PORT}/mcp"
    async with httpx.AsyncClient() as http_client:
        async with streamable_http_client(url, http_client=http_client) as (
            read,
            write,
            _get_session_id,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool("generate_workflow_id", {})
                answer = result.content[0].text
                assert answer.startswith("u_")
                assert len(answer) > 10

                result = await session.call_tool(
                    "list_container_items",
                    {
                        "urgap_storage_base_uri": f"file://{urgap._test_folder}/data/configs"
                    },
                )
                assert result.content[0].text == (
                    f'["file://{urgap._test_folder}/data/configs#credentials_lookup.json"]'
                )

                result = await session.call_tool(
                    "gcp_urgap_storage_pattern",
                    {"project_id": "my-gcp-project", "bucket": "my-bucket"},
                )
                assert result.content[0].text == "gcs://my-gcp-project/my-bucket"

                result = await session.call_tool(
                    "mylabdata_urgap_storage_pattern",
                    {
                        "server": "mylabdata-files.uat.corpnet2.com",
                        "equipment_id": "my-mld-project",
                        "task_id": "my-task-id",
                    },
                )
                assert result.content[0].text == (
                    "mylabdata://mylabdata-files.uat.corpnet2.com/my-mld-project/my-task-id"
                )

                result = await session.call_tool(
                    "ensure_urgap_uri_format",
                    {
                        "uris_to_check": [
                            "az-smb://myaccount/myshare/myfile.txt",
                            "/tmp/folder/dummy.txt",
                        ]
                    },
                )
                assert result.content[0].text == (
                    '["az-smb://myaccount/myshare#myfile.txt","file:///tmp/folder#dummy.txt"]'
                )
