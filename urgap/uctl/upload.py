"""Upload submodule of urgap.uctl."""

import logging
import pprint

from pathlib import Path

import click

from tqdm import tqdm

import urgap

logger = logging.getLogger(__name__)


@click.command()
@click.argument("folder")
@click.argument("storage_base_uri")
@click.argument("bucket_structure")
def upload_folder_click(
    folder: str,
    storage_base_uri: str,
    bucket_structure: str,
) -> None:
    """Upload the contents of a folder to a storage_base_uri with a given bucket structure.

    Object stores do not have real folders, but the concept is preserved for object naming
    and uniqueness within the bucket.

    Example:
        uctl upload folder ~/Download gcs://gcp-project-name/gcs-container-name subfolder/in/bucket

    This will create UFiles with UUris like:
        gcs://gsk-rd-ngs-sbx/urgap_test#subfolder/<filename>
    """
    upload_folder(
        folder=folder,
        bucket_structure=bucket_structure,
        storage_base_uri=storage_base_uri,
    )


def upload_folder(folder: str, bucket_structure: str, storage_base_uri: str) -> None:
    """Upload files from a folder into a new storage_base_uri.

    Args:
        folder: Path to the folder with files to upload.
        bucket_structure: Prefix for object name in the bucket.
        storage_base_uri: Target storage base UUri.
    """
    base_folder = Path(folder)
    all_files = urgap.UFileList.from_folder(base_folder)
    resulting_uris = []
    with tqdm(
        total=len(all_files),
        desc="Uploading",
        ncols=60,
        leave=False,
        dynamic_ncols=True,
        miniters=1,
    ) as pbar:
        for file in all_files:
            pbar.set_description(f"Processing file {file.object_name}")
            file.rebase(uri=f"{storage_base_uri}#{bucket_structure}/{file.object_name}")
            file.upload()
            resulting_uris.append(file.as_uri())
            pbar.update(1)
    logger.info(pprint.pformat("Upload finished, final uris:"))
    for uri in resulting_uris:
        msg = f"'{uri}'"
        logger.info(pprint.pformat(msg))


@click.group()
def upload() -> None:
    """Upload files or folders to object storage."""


upload.add_command(upload_folder_click, name="folder")
