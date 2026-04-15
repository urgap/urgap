import pandas as pd
import pytest
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession
import json
import httpx
import urgap


@pytest.mark.parametrize(
    "provide_uctl_server",
    [("FilterTabularToCSV:1.0.0", 41999)],
    indirect=["provide_uctl_server"],
)
@pytest.mark.asyncio
async def test_urgap_mcp_server_filter_csv(provide_uctl_server, tmp_dir):
    url = "http://localhost:41999/mcp"

    async with httpx.AsyncClient() as http_client:
        async with streamable_http_client(url, http_client=http_client) as (
            read,
            write,
            _get_session_id,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "FilterTabularToCSV_1_0_0",
                    {
                        "ufiles": [
                            f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}#unified_csvs/BSA1_xtandem_alanine_unified.csv",
                        ],
                        "unode_execution_parameters": {
                            "-q": "500 < `exp_mz` < 1000",
                        },
                        "output_urgap_storage_base_uri": f"file://{tmp_dir}",
                    },
                )
    result_list = json.loads(result.content[0].text)
    df = pd.read_csv(urgap.UFile(uri=result_list[0]).path)
    assert df["sequence_start"].sum() == 9925
    assert df.shape[0] == 31
