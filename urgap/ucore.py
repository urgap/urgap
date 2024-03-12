
import hashlib
import logging
import re
import shutil
import subprocess
from functools import partial
from pathlib import Path





    Args:

    Returns:
    """
    if hash_algorithm == "md5":
    else:
            f"Do not know how to identify output folder signature for {hash_algorithm}"
        )
    return signature is not None


def calculate_file_hash(
    hash_algorithm: str,
) -> str:

    Args:

    Returns:
    """





    Raises:
    """
        if wid_folder.exists():
            try:
                subprocess.call(["chmod", "-R", "0777", wid_folder])
                shutil.rmtree(wid_folder)

