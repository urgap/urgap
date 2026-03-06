"""Resources for MCP module of urgap."""

import urllib.parse

from mcp.server.fastmcp import FastMCP

import urgap

"""
Resources
---------

Application-controlled:

Data exposed by the application, e.g.
- Files
- Database records
- API responses
- urgap wid generation

Adapted from Mahesh Murag @ Antrophic
"""


def register_resources(server: FastMCP) -> None:
    """Register resources to the FastMCP server.

    Args:
        server (FastMCP): mcp fastmcp instance
    """

    @server.resource(
        "uu-greeting://{name}",
        name="Personal Greeting",
        description="A personalized uu-greeting using the name parameter",
        mime_type="text/plain",
    )
    def get_greeting(name: str) -> str:
        """Return a personalized uu-Greeting."""
        return f"Hello there {name}"

    @server.resource(
        "mylabdata-uat://{equipment_id}/{task_id}/{data_type}/{path}",
        name="urgap uri for a file in mylabdata uat",
        description="Urgap uri representation for a file in mylabdata uat.",
        mime_type="text/plain",
    )
    def generate_mld_uat(
        equipment_id: str,
        task_id: str,
        data_type: str,
        path: str,
    ) -> str:
        """Generate urgap file uri for mylabdata uat.

        Args:
            equipment_id (str): Equipment ID
            task_id (str): Task ID
            path (str): File Path (use urllib.parse.quote(value, safe="") to remove slashes).
            data_type (str, optional): File Extension. Will be mapped to uftypes. Optional

        For example:
        - "Generate a urgap uri for mylabdata uat, instrument_sap_id 354557, task_id 24-10000864-C4, data_type any.ANY and path dummy.txt"

        Returns:
            str: urgap file uri
        """
        possible_uftypes = urgap.instances.utree_querier.get_nodes_with_ext(data_type)
        if len(possible_uftypes) > 1:
            for _ in possible_uftypes:
                if _.startswith("any"):
                    data_type = _
                    break
        path = urllib.parse.unquote(path)
        return f"mylabdata://mylabdata-files.uat.corpnet2.com/{equipment_id}/{task_id}?uftype={data_type}#{path}"

    @server.resource(
        "mylabdata-uat-storage-base://{equipment_id}/{task_id}",
        name="urgap storage base for mylabdata uat",
        description="Urgap uri representation storage base for mylabdata uat.",
        mime_type="text/plain",
    )
    def generate_mld_uat_storage_base(equipment_id: str, task_id: str) -> str:
        """Generate urgap storage base uri for mylabdata uat.

        Args:
            equipment_id (str): Equipment ID
            task_id (str): Task ID

        Will be called for example like:
        - "please give me a mylabdata uat storage base uri for instrument_sap_id 354557 and task_id 24-10000864-C4"

        Returns:
            str: urgap uri storage base
        """
        return f"mylabdata://mylabdata-files.uat.corpnet2.com/{equipment_id}/{task_id}"

    @server.resource(
        "gcp-storage-base://{project_id}/{bucket}",
        name="urgap storage base for google cloud",
        description="Urgap uri representation storage base for google cloud.",
        mime_type="text/plain",
    )
    def generate_gcp_storage_base(project_id: str, bucket: str) -> str:
        """Generate urgap storage base uri for gcp.

        Args:
            project_id (str): Google project name
            bucket (str): Google bucket name

        Will be called for example like:
        - "please give me a gcp storage base uri for project id gsk-rd-dso-gcp-uat and bucket agentic-ai-demo"

        Returns:
            str: urgap uri storage base
        """
        return f"gcs://{project_id}/{bucket}"
