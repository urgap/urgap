import pandas as pd
import pytest

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

import urgap


@pytest.mark.parametrize(
    "provide_uctl_server",
    [("FilterTabularToCSV:1.0.0", 41999)],
    indirect=["provide_uctl_server"],
)
@pytest.mark.asyncio
async def test_urgap_mcp_server_filter_csv(provide_uctl_server, tmp_dir):
    url = "http://localhost:41999/sse"

    async with sse_client(f"{url}") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            result = await client.call_tool(
                "FilterTabularToCSV_1_0_0",
                {
                    "ufiles": [
                        f"file://{urgap._test_folder}/data?uftype={urgap.uftypes.any.CSV}#unified_csvs/BSA1_xtandem_alanine_unified.csv",
                    ],
                    "tool_parameter": {
                        "-q": "500 < `exp_mz` < 1000",
                    },
                    "output_urgap_storage_base_uri": f"file://{tmp_dir}",
                },
            )
    df = pd.read_csv(urgap.UFile(uri=result.content[0].text).path)
    assert df["sequence_start"].sum() == 9925
    assert df.shape[0] == 31
