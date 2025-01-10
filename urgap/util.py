
import binascii
import concurrent.futures
import logging
import os
import re

from packaging.version import Version


def sense_compression_format(file: os.PathLike) -> str:


    Args:

    Returns:
    """
    expected_hex_for_tar = "00" * 1024
    hex_eof_marker = None
        signature = str(binascii.hexlify(f.read(300)))[2:-1]
        try:
            f.seek(-1024, 2)
            eof_marker = f.read(1024)
            hex_eof_marker = binascii.hexlify(eof_marker).decode("ascii")
        except OSError:
            pass
    if signature.startswith("1f8b"):
        compression_format = "gz"
    elif hex_eof_marker == expected_hex_for_tar:
        if signature[257 * 2 :].startswith("7573746172"):
            compression_format = "tar"
        else:
            compression_format = "split_tar"
    elif signature[257 * 2 :].startswith("7573746172"):
        compression_format = "split_tar"
    elif signature.startswith("504b0304"):
        compression_format = "zip"
    elif signature.startswith("425a68"):
        compression_format = "bz2"
    else:
        compression_format = "UNKNOWN"
    return compression_format


def extract_from_string(any_string: str, regex_pattern: str) -> list:

    Args:

    Returns:
    """


def execute_threaded_function(
    func: Callable,
    number_of_threads: int = 8,

    Args:
    """


    if len(args_list) == 0:
        results = None
    else:
        first_is_nested = _is_nested(args_list[0])
        if not all(_is_nested(arg) == first_is_nested for arg in args_list):
        with concurrent.futures.ThreadPoolExecutor(
        ) as executor:
            if first_is_nested:
                results = list(executor.map(lambda args: func(*args), args_list))
            else:
                results = list(executor.map(func, args_list))
    return results



    Args:

    Returns:
    """
    if ":" not in item:
        return (item, 1, None)
    tool, version = item.split(":")
    is_latest = -1 if version == "latest" else 0
    parsed_version = Version(version) if version != "latest" else None
    return (tool, is_latest, parsed_version)


def get_next_port(
) -> int:

    Args:

    Returns:
    """
    if is_lastest is True:
        if (last_assigned_port % 10) != 0:
            return ((last_assigned_port // 10) + 1) * 10
    next_port = last_assigned_port + 1
    if next_port % 10 == 0:
        next_port += 1
    if next_port > last_port:
            "Not enough ports available. Increase number of available ports in config."
        )
    return next_port