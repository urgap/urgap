"""Prompts for MCP module of urgap."""

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
    async def google_bucket_urgap_storage_base_uri_pattern(
        project_id: str,
        bucket: str,
    ) -> Prompt:
        """Google bucket urgap storage base uri pattern.

        Args:
            project_id (str): Google Project ID
            bucket (str): Gcs Bucket name

        Returns:
            Prompt: Pattern of the goolge urgap storage pattern
        """
        return Prompt(
            name="google_bucket_urgap_storage_base_uri_pattern",
            messages=[
                base.AssistantMessage(
                    content={
                        "type": "text",
                        "text": f"gcs://{project_id}/{bucket}",
                    },
                ),
            ],
            arguments=[
                {
                    "name": "project_id",
                    "description": "Google project id",
                    "required": True,
                },
                {
                    "name": "bucket",
                    "description": "Google bucket name",
                    "required": True,
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
                                                        // Example: 'gcs://{project_id}/{bucket}'
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
                        "storage_base_uri": "gcs://<my-project-id>/<my-container>",
                    }
                }
            """

        _for_later = """
        "unode_parameters": {        // Parameters specific to the UNode

                "additional_filters": dict|None,  // Optional: Additional filters during input file filtering
                                                // Format: {urgap.uftypes.test.TEST_FILE1: {"tags": {"QC": "good"}}}

                "dry_run": bool,                // Optional: Whether execution is skipped (default: false)
                                                // Not implemented yet

                "force": bool,                  // Optional: Whether execution is forced (default: false)

                "override_folder_creation": bool,  // Optional: Skip folder creation (default: false)
                                                // Not sure if still used

                "prefix": str|None,             // Optional: Additional prefix for all object names
                                                // Example: "ROS1_" would yield ROS1_<input_file_ids_md5>_0.test_file2

                "run_folder_name": str|None,    // Optional: Override folder name creation
                                                // Default: node name + re-run param md5

                "skip_data_versioning": bool,   // Optional: Skip versioning in folder names (default: false)
                                                // Results in: test_node_v1/<input_file_ids_md5>_0.test_file2

                "skip_pre_checks": bool,        // Optional: Skip pre-checks before execution (default: false)
                                                // Pre-checks include 3rd party installation verification

                "storage_base_uri": str|None,   // Optional: Storage base URI for output files
                                                // Example: "gcs://<project>/<bucket>"

                "record_skipped_runs": bool,    // Deprecated: All execution info will be stored (default: false)

                "remove_temporary_files": bool, // Optional: Delete temporary files from wrapper (default: false)

                "retain_uftypes": bool,         // Optional: Retain output file uftypes regardless of wrapper definition (default: false)

                "file_io_timeout": int|None,    // Optional: Timeout in seconds for re-initializing ufile list
                                                // Helpful if IO backend times out during long processing
                                                // None = skip re-init

                "remote_url": str|None,         // Optional: Remote execution URL (e.g., "localhost")
                                                // Requires uctl upi_server (API) on remote host
                                                // Only for wrappers with api_port in UMETA

                "remote_execution_timeout": int, // Optional: Timeout for remote execution in seconds (default: 7200)
                                                // Default: 2 hours

                "latest_exe_paths": dict|None   // Optional: Explicit exe paths when using latest tag
                                                // Format: {'msfragger:latest': "/path/to/exe/in_upi_server"}
            }
        """

        return Prompt(
            name="urun_default_dict",
            description="Default urgap urun_dict requireed to run all urgap tools.",
            messages=[
                base.AssistantMessage(
                    content={"type": "text", "text": tool_docs},
                ),
            ],
        )
