
import logging
import pprint

from pathlib import Path

import click

from tqdm import tqdm



@click.command()
@click.argument("folder")
@click.argument("storage_base_uri")
@click.argument("bucket_structure")
def upload_folder_click(
) -> None:
    """Upload the contents of a folder to a storage_base_uri with a given bucket structure.

    Object stores do not have real folders, but the concept is preserved for object naming
    and uniqueness within the bucket.

    Example:
        uctl upload folder ~/Download gcs://gcp-project-name/gcs-container-name subfolder/in/bucket

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
    """
    base_folder = Path(folder)
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
    for uri in resulting_uris:
        msg = f"'{uri}'"