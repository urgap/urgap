"""MCP Tools module of urgap."""

import logging

import urgap

logger = logging.getLogger(__name__)

"""
Tools
-----

Model-controlled:

Functions invoked by he model, e.g.
- retrieve / search
- send message
- update DB records
- run urgap node

Adapted from Mahesh Murag @ Antrophic
"""


def list_container_times(
    urgap_storage_base_uri: str,
    regex_pattern_string: str | None = None,
    limit: int = 1000,
) -> list:
    """List all files in container defined by a urgap storage base uri.

    Args:
        urgap_storage_base_uri (str): a urgap storage base uri string, e.g. using the tools google_bucket_urgap_storage_base_uri_pattern or mylabdata_urgap_storage_base_uri_pattern
        regex_pattern_string (str | None, optional): A Python regex to filter the listed files. Defaults to None.
        limit (int, optional): A limit of how many files should be returned. Defaults to 1000.

    for example:
    - list all files in mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-10000864-C4
    - Generate a urgap storage base uri for mylabdata uat, instrument_sap_id 354557, task_id 24-10000864-C4 and then use this uri to list all files in the container
    - Generate a urgap storage base uri for mylabdata uat, instrument_sap_id 354557, task_id 24-10000864-C4 and then use this uri to list all files in the container and use a Python regex that matches files that end on .csv to limit the output.
    - Generate a urgap gcp storage base uri for project_id gsk-rd-dso-gcp-uat and bucket agentic-ai-demo and then list all files.

    Returns:
        list: A list of urgap ufile uris
    """
    msg = f"Listing container Items with {urgap_storage_base_uri}"
    logger.info(msg)

    return urgap.UFile(f"{urgap_storage_base_uri}#dummy.txt").list_container_items(
        pattern=regex_pattern_string,
        limit=limit,
        full_string=True,
    )


def calculate_nana(
    weight: float,
    height: float,
) -> float:
    """Calculate the nana_index given height in meters and weight in Kg.

    Returns:
        float: nana_index
    """
    return weight / (height**2)


def generate_workflow_id() -> str:
    """Generate an URGAP workflow ID - also known as wid.

    Returns:
      str: the workflow id
    """
    return urgap.uwid_obj.generate_wid()


def gcp_urgap_storage_pattern(project_id: str, bucket: str) -> str:
    """Generate urgap_storage_base_uri for google buckets.

    Args:
        project_id (str): gcp project
        bucket (str): gcp bucket

    Returns:
        str: urgap_storage_base_uri that can be used to, e.g. list_container_items or as
         part of the urgap processing node input ufile list.
    """
    return f"gcs://{project_id}/{bucket}"


def mylabdata_urgap_storage_pattern(equipment_id: str, task_id: str) -> str:
    """Generate urgap_storage_base_uri for mylabdata in UAT.

    Args:
        equipment_id (str): mylabdata equipment id
        task_id (str): mylabdata task_id

    Returns:
        str: urgap_storage_base_uri that can be used to, e.g. list_container_items or as
         part of the urgap processing node input ufile list.
    """
    return f"mylabdata://mylabdata-files.uat.corpnet2.com/{equipment_id}/{task_id}"


"""
TOOL IDEAS

List all nodes that can consume certain file types
List all nodes that can produce certain file types
Find node by description.
"""
