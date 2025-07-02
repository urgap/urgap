"""Prompts for MCP module of urgap2."""

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.types import Prompt

"""
Prompts
-------

User-controlled:

Predefined tempaltes for AI interactions, e.g.
- documenta Q&A
- Transcription summary
- Output as JSON
- default urun_dict format

Adapted from Mahesh Murag @ Antrophic

The client logic for deciding when to inject prompts can vary significantly
based on the implementation, but here are the common patterns and strategies:
"""


def register_prompts(server: FastMCP) -> None:
    """Register prompts to the FastMCP server.

    Args:
        server (FastMCP): mcp fastmcp instance
    """

    @server.prompt()
    async def mylabdata_urgap_storage_base_uri_pattern(
        equipment_id: str,
        task_id: str,
        env: str = "uat",
    ) -> Prompt:
        """Mylabdata urgap storage base uri pattern.

        Args:
            equipment_id (str): Mylabdata equipment ID
            task_id (str): Mylabdata Task ID
            env (str, optional): Mylabdata environment uat|prod. Defaults to "uat".

        Returns:
            Prompt: Pattern of the mylabdata urgap storage pattern
        """
        env_normalized = env.upper() if env is not None else "UAT"

        if env_normalized in ["UAT", "DEV"]:
            content = (
                f"mylabdata://mylabdata-files.uat.corpnet2.com/{equipment_id}/{task_id}"
            )
        elif env_normalized == "PROD":
            content = (
                f"mylabdata://mylabdata-files.corpnet2.com/{equipment_id}/{task_id}"
            )
        else:
            content = "The environment {env_normalized} is unknown, please specify 'uat' or 'prod'."

        return Prompt(
            name="mylabdata_urgap_storage_base_uri_pattern",
            description=f"Mylabdata urgap storage base uri pattern for {equipment_id} {task_id} in {env}",
            messages=[
                base.AssistantMessage(
                    content={"type": "text", "text": content},
                ),
            ],
            arguments=[
                {
                    "name": "equipment_id",
                    "description": "Mylabdata equipment_id",
                    "required": True,
                },
                {
                    "name": "task_id",
                    "description": "Mylabdata task_id",
                    "required": True,
                },
                {
                    "name": "env",
                    "description": "Mylabdata environment, that is uat or prod",
                    "required": False,
                    "default": "uat",
                },
            ],
        )

    @server.prompt()
    async def urun_default_dict() -> Prompt:
        """Provide default urgap URun Dict used for urgap node execution."""
        tool_docs = """
                The urgap configuration dictionary has the following structure:

                {
                    "parameters": {           // Parameters specific to the wrappers or wrapped executables
                        <tool name> : {       // urgap tool name e.g. 'FilterTabularToCSV:1.0.0'
                            <tool_parameter_key_1> : <tool_parameter_value_1>,  // e.g. "-q": "500 < `exp_mz` < 1000"
                            ...
                        },

                    },
                    "unode_parameters": {
                        "storage_base_uri": str|None,   // Optional: Storage base URI for output files
                                                        // this can be handled by tools that generate urgap storage uri.

                        "force": bool,                  // Optional: Whether execution is forced (default: false)

                    },
                    "wid": str,                  // Urgap Workflow ID, format: u_<adjective>-<noun>-<verb>-<adjective>-<noun>
                                                // Generated via the generate wid tool.
                                                // can also be passed as parameter.
                }

                Example usage:
                {
                    "parameters": {
                        "FilterTabularToCSV:1.0.0": {
                            "-q": "500 < `exp_mz` < 1000"
                        },
                    "user_dict": {
                        "experiment_id": "exp_123", "operator": "john_doe"
                    },
                    "unode_parameters": {
                        "force": true,
                    }
                }
            """

        "unode_parameters": {        // Parameters specific to the UNode















