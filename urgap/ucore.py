
import contextlib
import hashlib
import logging
import re
import shutil
import subprocess

from collections.abc import Iterable
from functools import partial
from pathlib import Path

import requests



def folder_has_uparam_signature(folder: Path) -> bool:
    """Check if a folder has the uparam-generated signature.

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
    """Calculate the file hash using the specified algorithm.

    Args:
        input_file: Path to the file to hash.
        hash_algorithm: Hash algorithm supported by hashlib (e.g., 'md5', 'sha256').

    Returns:
        Hexadecimal digest of the file. Returns 'no file - no hash' if the file does not exist.

    References:
        Adapted from Raymond Hettinger's solution:
        https://stackoverflow.com/questions/7829499/using-hashlib-to-compute-md5-digest-of-a-file-in-python-3
    """
    if input_file.exists():
            digest = getattr(hashlib, hash_algorithm)()
            for buffer in iter(partial(f.read, 1024), b""):
                digest.update(buffer)
        return digest.hexdigest()
    return "no file - no hash"


def calculate_string_hash(hashable_iterable: Iterable, hash_algorithm: str) -> str:
    """Calculate the string hash using the specified algorithm.

    Args:
        hashable_iterable: Iterable to compute checksum for.
        hash_algorithm: Hash algorithm supported by hashlib (e.g., 'md5', 'sha256').
    """
    digest = getattr(hashlib, hash_algorithm)()
    for i in hashable_iterable:
        digest.update(i)
    return digest.hexdigest()


def clean_up_scratch_space() -> None:
    """Delete all temporary scratch folders created during the current session.


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
    """Append a query string to the URI before the fragment.

    If the URI already contains a query string, the new query is appended directly.
    Otherwise, a '?' is added before the query.

    Arguments:
        uri: The original URI in the format 'base_uri#fragment'.
        query: The query string to append (e.g., 'key=value').

    Returns:
        str: The updated URI with the query appended before the fragment.
    """
    (storage_base_uri, object_name) = uri.split("#")
    if "?" in storage_base_uri:
        storage_base_uri += "&" + query
    else:
        storage_base_uri += "?" + query
    return f"{storage_base_uri}#{object_name}"