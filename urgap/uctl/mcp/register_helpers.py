"""MCP helpers for registering tools and unodes of urgap2."""

import logging

from fastmcp import FastMCP

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
        server.tool(
            un.run_node_as_mcp_tool,
            name=unode_name,
            description=build_tool_description(unode_name, un),
        )


def build_tool_description(unode_name: str, unode: urgap.UNodeBase) -> str:
    """Build the mcp tool description for a unode.

    The parameter descriptions themselves are derived by FastMCP from the
    signature and docstring of ``run_node_as_mcp_tool``, so only the
    unode specific context is assembled here.

    Args:
        unode_name (str): mcp safe name of the unode, e.g. ``FilterTabularToCSV_1_0_0``
        unode (urgap.UNodeBase): initialized unode instance

    Returns:
        str: description shown to the model for this tool.
    """
    return f"""
{unode.__doc__}
\n {unode.run_node_as_mcp_tool.__doc__}
\n This is an example of the parameters for {unode_name}: {unode.META_INFO["parameter_examples"]}"
"""
