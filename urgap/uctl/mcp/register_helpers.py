"""MCP helpers for registering tools and unodes of urgap2."""

import functools
import logging

from mcp.server.fastmcp import FastMCP

import urgap

logger = logging.getLogger(__name__)


def register_unodes(server: FastMCP, nodes_list: list) -> None:
    """Register unodes to the FastMCP server.

    Args:
        server (FastMCP): mcp fastmcp instance
        nodes_list (list): list of urgap nodes to register.
    """
    for unode in nodes_list:
        if "latest" in unode:
            continue
        un = urgap.init_unode(unode)
        if un.META_INFO.get("parameter_examples", None) is None:
            msg = f"\n\nCannot use {unode} as mcp tools, because `parameter_example` are missing in META_INFO!\n"
            logger.warning(msg)
            continue

        unode_name = unode.replace(":", "_").replace(".", "_")

        def _make_tool(bound_node, param_examples, input_uftypes):
            @functools.wraps(bound_node.run_node_as_mcp_tool)
            def tool_fn(
                ufiles: list[str],
                params: dict,
                force: bool = False,
                output_urgap_storage_base_uri: str | None = None,
                latest_exe_path: str | None = None,
                workflow_id: str | None = None,
            ) -> list:
                return bound_node.run_node_as_mcp_tool(
                    ufiles=ufiles,
                    params=params,
                    force=force,
                    output_urgap_storage_base_uri=output_urgap_storage_base_uri,
                    latest_exe_path=latest_exe_path,
                    workflow_id=workflow_id,
                )

            tool_fn.__doc__ = (
                bound_node.run_node_as_mcp_tool.__doc__
                + f"\n    Node-specific params example: {param_examples}"
                + f"\n    Input file types (uftypes): {input_uftypes}"
            )
            return tool_fn

        server.tool(name=unode_name)(
            _make_tool(
                un, un.META_INFO["parameter_examples"], un.META_INFO["input_uftypes"],
            ),
        )
