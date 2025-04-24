
import contextlib
import hashlib
import logging
import re
import shutil
import subprocess

from functools import partial
from pathlib import Path

import requests





    Args:

    Returns:
    """
    if hash_algorithm == "md5":
    else:
        msg = (
            f"Do not know how to identify output folder signature for {hash_algorithm}"
        )
        raise NotImplementedError(msg)
    return signature is not None


def calculate_file_hash(
    hash_algorithm: str,
) -> str:

    Args:

    Returns:
    """




def clean_up_scratch_space() -> None:

    Raises:
    """
        if wid_folder.name != wid:
            wid_folder /= wid
        if wid_folder.exists():
            try:
                subprocess.call(["chmod", "-R", "0777", wid_folder])
                shutil.rmtree(wid_folder)
            except OSError:
                msg = f"Could not delete {wid_folder} - OSError ..."


def shutdown_local_upi_servers(force: bool = False) -> None:

    Args:
    """
            run_payload = {"be humble": "sit down"}
            run_url = f"http://127.0.0.1:{port}/v1/terminate"
            with contextlib.suppress(requests.exceptions.RequestException):
                requests.post(
                    run_url,
                    json=run_payload,
                    timeout=(
                    ),
                )


def shutdown_telemetry() -> None:
    """Shut down Utelemetry servers."""