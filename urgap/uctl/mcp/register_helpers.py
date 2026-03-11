"""MCP helpers for registering tools and unodes of urgap2."""

import logging

from mcp.server.fastmcp import FastMCP

import urgap

logger = logging.getLogger(__name__)


def register_tools(server: FastMCP) -> None:
    """Register tools to the FastMCP server.

    Args:
        server (FastMCP): mcp fastmcp instance
    """
    from urgap.uctl.mcp.tools import (
        calculate_nana,
        gcp_urgap_storage_pattern,
        generate_workflow_id,
        list_container_times,
        mylabdata_urgap_storage_pattern,
    )

    tools = [
        {"function": list_container_times, "tool_name": "list_container_times"},
        {"function": generate_workflow_id, "tool_name": "generate_workflow_id"},
        {
            "function": gcp_urgap_storage_pattern,
            "tool_name": "gcp_urgap_storage_pattern",
        },
        {
            "function": mylabdata_urgap_storage_pattern,
            "tool_name": "mylabdata_urgap_storage_pattern",
        },
    ]
    _to_be_implemented = [
        {"function": calculate_nana, "tool_name": "nana_index"},
        {
            "function": "extend_uri_list_with_uftype",
            "tool_name": "extend_uri_list_with_uftype",
        },
        {
            "function": "understand_urgap_node_parameters",
            "tool_name": "understand_urgap_node_parameters",
        },
    ]

    for tool_item in tools:
        msg = "Registering {tool_name}".format(**tool_item)
        logger.info(msg)

        server.add_tool(
            tool_item["function"],
            tool_item["tool_name"],
            tool_item["function"].__doc__,
        )


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
        server.add_tool(
            un.run_node_as_mcp_tool,
            f"{unode_name}",
            f"""{unode_name}:

    {un.run_node_as_mcp_tool.__doc__}

    This is an example of the parameters for {unode_name}:
        {un.META_INFO["parameter_examples"]}

    Input file types (uftypes) are:
        {un.META_INFO["input_uftypes"]}

            """,
        )
