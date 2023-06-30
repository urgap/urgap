
from pathlib import Path

import click



@click.command()
@click.argument("folder")
@click.argument("storage_base_uri")
@click.argument("bucket_structure")



    """



    Args:
    """
    base_folder = Path(folder)
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