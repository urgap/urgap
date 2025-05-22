
import contextlib
import hashlib
import logging
import re
import shutil
import subprocess

from functools import partial
from pathlib import Path

import requests



def folder_has_uparam_signature(folder: Path) -> bool:

        `<node_name>_<hash_of_parameters_triggering_rerun>`

    Args:
        folder: Folder path or folder name to inspect.

    Returns:
        True if the folder matches the uparam signature; False otherwise.

    Raises:
        NotImplementedError: If the configured hash algorithm is unsupported.
    """
    if hash_algorithm == "md5":
        signature = re.search(r"_[0-9a-z]{32}$", folder.name)
    else:
        msg = (
            f"Do not know how to identify output folder signature for {hash_algorithm}"
        )
        raise NotImplementedError(msg)
    return signature is not None


def calculate_file_hash(
    input_file: Path,
    hash_algorithm: str,
) -> str:

    Args:
        input_file: Path to the file to hash.
        hash_algorithm: Hash algorithm supported by hashlib (e.g., 'md5', 'sha256').

    Returns:

    References:
        Adapted from Raymond Hettinger's solution:
        https://stackoverflow.com/questions/7829499/using-hashlib-to-compute-md5-digest-of-a-file-in-python-3
    """
    if input_file.exists():
            digest = getattr(hashlib, hash_algorithm)()
            for buffer in iter(partial(f.read, 1024), b""):
                digest.update(buffer)
        return digest.hexdigest()




def clean_up_scratch_space() -> None:


    Raises:
        OSError: Logs a warning if a scratch directory cannot be deleted.
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
    """Shuts down all locally running UPI servers.

    Args:
        force: If True, forces the shutdown of servers regardless of configuration.
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


def append_query_to_uri(uri: str, query: str) -> str:
    if "?" in storage_base_uri:
    else:
        storage_base_uri += "?" + query
    return f"{storage_base_uri}#{object_name}"