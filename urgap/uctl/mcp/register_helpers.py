"""MCP helpers for registering tools and unodes of urgap2."""

import inspect
import logging

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec

from mcp.server.fastmcp import FastMCP

import urgap

logger = logging.getLogger(__name__)
P = ParamSpec("P")


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
        fn = make_tool(un.run_node_as_mcp_tool, unode_name, un)
        server.tool()(fn)


def make_tool(method: Callable, unode_name: str, unode: urgap.UNodeBase) -> Callable:
    """Create a fastmcp tool wrapper."""

    @wraps(method)
    def wrapper(*args: dict, **kwargs: P.kwargs) -> Callable:
        return method(*args, **kwargs)

    wrapper.__name__ = unode_name
    wrapper.__doc__ = f"""
{unode.__doc__}
\n {method.__doc__}
\n This is an example of the parameters for {unode_name}: {unode.META_INFO["parameter_examples"]}"
"""
    wrapper.__signature__ = inspect.signature(method)
    return wrapper
