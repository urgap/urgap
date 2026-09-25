"""MCP Tools module of urgap."""

import logging

from pathlib import Path
from urllib.parse import urlparse

import fastmcp

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

name = "urgap tools mcp server"
mcp_tools_server = fastmcp.FastMCP(name)


@mcp_tools_server.tool()
async def list_container_items(
    urgap_storage_base_uri: str,
    pattern: str | None = None,
    limit: int | None = None,
) -> list:
    """List all files in container defined by a urgap storage base uri.

    Args:
        urgap_storage_base_uri: a urgap storage base uri string, e.g. using the tools google_bucket_urgap_storage_base_uri_pattern or mylabdata_urgap_storage_base_uri_pattern
        pattern: A string to filter the listed files. Defaults to None.
            when filtering for subfolders, use e.g. "subfolder/1/2/3"
        limit: A limit of how many files should be returned.

    for example:
    - list all files in mylabdata://mylabdata-files.uat.corpnet2.com/354557/24-10000864-C4
    - Generate a urgap storage base uri for mylabdata uat, instrument_sap_id 354557, task_id 24-10000864-C4 and then use this uri to list all files in the container
    - Generate a urgap storage base uri for mylabdata uat, instrument_sap_id 354557, task_id 24-10000864-C4 and then use this uri to list all files in the container and use a Python regex that matches files that end on .csv to limit the output.
    - Generate a urgap gcp storage base uri for project_id gsk-rd-dso-gcp-uat and bucket agentic-ai-demo and then list all files.

    Returns:
        list: A list of all urgap ufile uris from inside the container.
    """
    msg = f"Listing container Items with {urgap_storage_base_uri}"
    logger.info(msg)
    file_uris = urgap.UFile(
        f"{urgap_storage_base_uri}#dummy.txt",
    ).io.list_container_items(
        pattern=pattern,
        limit=limit,
        full_string=True,
    )
    msg = f"Found {len(file_uris)} files in container. All files: {file_uris}."
    logger.info(msg)
    return file_uris


@mcp_tools_server.tool()
async def calculate_nana(
    weight: float,
    height: float,
) -> float:
    """Calculate the nana_index given height in meters and weight in Kg.

    Returns:
        float: nana_index
    """
    return weight / (height**2)


@mcp_tools_server.tool()
async def generate_workflow_id() -> str:
    """Generate an URGAP workflow ID - also known as wid.

    Returns:
      str: the workflow id
    """
    return urgap.uwid_obj.generate_wid()


@mcp_tools_server.tool()
async def gcp_urgap_storage_pattern(project_id: str, bucket: str) -> str:
    """Generate urgap_storage_base_uri for google buckets.

    Args:
        project_id (str): gcp project
        bucket (str): gcp bucket

    Returns:
        str: urgap_storage_base_uri that can be used to, e.g. list_container_items or as
         part of the urgap processing node input ufile list.
    """
    return f"gcs://{project_id}/{bucket}"


@mcp_tools_server.tool()
async def mylabdata_urgap_storage_pattern(
    server: str,
    equipment_id: str,
    task_id: str,
) -> str:
    """Generate urgap_storage_base_uri for mylabdata.

    Args:
        server (str): mylabdata server, e.g. "mylabdata-files.uat.corpnet2.com"
        equipment_id (str): mylabdata equipment id (e.g. "354557")
        task_id (str): mylabdata task_id (e.g. "24-10000864-C4") Important: cannot contain "/" characters, otherwise the generated URI will not be valid.
            everything after the first "/" character in task_id must go into pattern parameter of list_container_items function.

    Returns:
        str: urgap_storage_base_uri that can be used to, e.g. list_container_items or as
         part of the urgap processing node input ufile list.
    """
    return f"mylabdata://{server}/{equipment_id}/{task_id}"


@mcp_tools_server.tool()
async def azure_bucket_urgap_storage_pattern(
    bucket: str,
    container: str,
) -> str:
    """Generate urgap_storage_base_uri for azure bucket.

    Args:
        bucket (str): azure bucket, e.g. "dsoazdevsa.blob.core.windows.net"
        container (str): container name in the azure bucket, e.g. "dev"
            everything after the first "/" character in container must go into pattern parameter of list_container_items function.

    Returns:
        str: urgap_storage_base_uri that can be used to, e.g. list_container_items or as
         part of the urgap processing node input ufile list.
    """
    return f"azure://{bucket}/{container}"


@mcp_tools_server.tool()
async def ensure_urgap_uri_format(uris_to_check: list[str]) -> list:
    """Ensure that all file and uris related to urgap operations use the correct urgap URI format.

    Always run this on urgap uris, locations, containers and so on before any urgap action.

    Args:
        uris_to_check: List of storage_base_uri paths as strings, e.g. "file:///home/user/data"

    Returns:
        list: List of file paths as strings in urgap URI format, e.g. "file:///home/user/data"
    """
    urgap_formatted_uris = []
    for file in uris_to_check:
        unparsed_file = urlparse(file)
        file_with_scheme = f"file://{file}" if unparsed_file.scheme == "" else file
        if "#" not in file_with_scheme and "." in Path(file_with_scheme).name:
            path, fragment = file_with_scheme.rsplit("/", 1)
            file_with_fragment = f"{path}#{fragment}"
        else:
            file_with_fragment = file_with_scheme
        urgap_formatted_uris.append(file_with_fragment)
    msg = f"Formatted these storage_base_uris {uris_to_check} into following urgap storage_base_uris {urgap_formatted_uris}"
    logger.info(msg)
    return urgap_formatted_uris


@mcp_tools_server.tool()
async def prepare_urgap_uris_for_beacon_run(urgap_uris: list[str]) -> list[str]:
    """Prepare URGAP URIs for Beacon imaging unode execution by adding appropriate uftype parameters.

    Args:
        urgap_uris (List[str]): List of URGAP URIs as strings from beacon imaging storage (Azure SMB)

    Returns:
        List[str]: List of URGAP URIs with proper uftype parameters for beacon unode processing

    Example queries:
        - Prepare beacon imaging files from az-smb://ie1fsnrdsac01.file.core.windows.net/rd-bpr-beacon/DataSessions/D115928 for device D115928
        - Format beacon URIs for device SpotLight_Hu_Lambda with proper uftypes
        - Process beacon imaging files and add uftype for unode execution
    """
    _tmp = []
    parts = urgap_uris[0].split("/")
    idx = parts.index("DataSessions")
    device_id = parts[idx + 1]
    msg = f"Extracted device_id {device_id} from URIs for beacon run preparation. Got {len(urgap_uris)} uris"
    logger.info(msg)
    for az_smb_file in urgap_uris:
        msg = f"Processing {az_smb_file} ..."
        logger.info(msg)
        az_smb_file_new = az_smb_file.replace("#", "/")
        pre_device_id, post_device_id = az_smb_file_new.split("/" + device_id + "/")
        if post_device_id.endswith(".tag"):
            continue
        if post_device_id.endswith("OptoSelect 1750b.XML"):
            _tmp.append(
                f"{pre_device_id}?uftype={urgap.uftypes.beacon.OPTOSELECT_XML}#{device_id}/{post_device_id}",
            )
        elif post_device_id.endswith(".XML"):
            _tmp.append(
                f"{pre_device_id}?uftype=.essay.xml#{device_id}/{post_device_id}",
            )
        elif post_device_id.endswith(".tiff"):
            _tmp.append(
                f"{pre_device_id}?uftype=.image.tiff#{device_id}/{post_device_id}",
            )
    msg = f"Processed {len(_tmp)} beacon URIs."
    logger.info(msg)
    if len(_tmp) != 24:
        msg = f"Expected 24 files after processing, but got {len(_tmp)}. Check the input URIs and device_id."
        logger.error(msg)
    return _tmp


"""
TOOL IDEAS

List all nodes that can consume certain file types
List all nodes that can produce certain file types
Find node by description.
"""
