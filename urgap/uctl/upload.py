
from pathlib import Path

import click

from tqdm import tqdm



@click.command()
@click.argument("folder")
@click.argument("storage_base_uri")
@click.argument("bucket_structure")
def upload_folder_click(
) -> None:



    """


def upload_folder(folder: str, bucket_structure: str, storage_base_uri: str) -> None:

    Args:
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
            pbar.update(1)