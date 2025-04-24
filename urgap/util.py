
import binascii
import concurrent.futures
import logging
import os
import re

from collections.abc import Callable

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
            msg = f"{file} is last file of split tar"
    elif signature[257 * 2 :].startswith("7573746172"):
        compression_format = "split_tar"
        msg = f"{file} is first file of split tar"
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
    return re.findall(regex_pattern, any_string)


def execute_threaded_function(
    func: Callable,
    number_of_threads: int = 8,
) -> list:

    Args:
    """

    def _is_nested(arg: str | list | tuple) -> bool:
        return isinstance(arg, list | tuple)

    if len(args_list) == 0:
        msg = f"Can't execute function without args! Args list is {args_list}"
        results = None
    else:
        first_is_nested = _is_nested(args_list[0])
        if not all(_is_nested(arg) == first_is_nested for arg in args_list):
            msg = "Inconsistent nesting: All elements must be either nested or not nested."
            raise ValueError(msg)
        with concurrent.futures.ThreadPoolExecutor(
        ) as executor:
            if first_is_nested:
                results = list(executor.map(lambda args: func(*args), args_list))
            else:
                results = list(executor.map(func, args_list))
    return results


def sort_versions(item: str) -> tuple:

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
        return last_assigned_port + 10
    next_port = last_assigned_port + 1
    if next_port % 10 == 0:
        next_port += 1
    if next_port > last_port:
        msg = (
            "Not enough ports available. Increase number of available ports in config."
        )
        raise IndexError(msg)
    return next_port