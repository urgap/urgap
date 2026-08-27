"""Util module of urgap."""

import binascii
import concurrent.futures
import importlib
import inspect
import logging
import os
import pkgutil
import re

from collections.abc import Callable, Iterator
from types import ModuleType
from typing import TypeVar

from packaging.version import Version

logger = logging.getLogger(__name__)

T = TypeVar("T")


def iter_public_modules(
    pkg_name: str,
    ignore_prefix: str | None = "_",
) -> Iterator[ModuleType]:
    """Import and yield each top-level, non-package module in pkg_name.

    Args:
        pkg_name: Dotted name of the package to scan.
        ignore_prefix: Skip module names starting with this prefix. Pass None to import all.
    """
    pkg = importlib.import_module(pkg_name)
    for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
        if ispkg or (ignore_prefix and modname.startswith(ignore_prefix)):
            continue
        full_name = f"{pkg_name}.{modname}"
        try:
            yield importlib.import_module(full_name)
        except ImportError:
            logger.debug(
                "Skipping module '%s' -- could not be imported.",
                full_name,
                exc_info=True,
            )


def discover_backend_classes(
    namespace_package: str,
    base_class: type[T],
    marker_attr: str,
) -> dict[str, type[T]]:
    """Scan a namespace package for base_class subclasses, keyed by marker_attr."""
    registry: dict[str, type[T]] = {}
    for module in iter_public_modules(namespace_package):
        for _, obj in inspect.getmembers(module, inspect.isclass):
            marker_value = getattr(obj, marker_attr, None)
            if (
                issubclass(obj, base_class)
                and obj is not base_class
                and obj.__module__ == module.__name__
                and marker_value
            ):
                if marker_value in registry:
                    msg = (
                        f"Duplicate backend registration for {marker_value!r}: "
                        f"{registry[marker_value]} and {obj}"
                    )
                    raise ValueError(msg)
                registry[marker_value] = obj
    return registry


def sense_compression_format(file: os.PathLike) -> str:
    """Determine the format of a compressed file.

    Supports tar.gz, zip, and bz2.

    Args:
        file: Path to the file.

    Returns:
        The detected compressed file format as a string (e.g. "gz", "zip", "tar", "bz2", or "UNKNOWN").
    """
    expected_hex_for_tar = "00" * 1024
    hex_eof_marker = None
    with file.open("rb") as f:
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
            logger.info(msg)
    elif signature[257 * 2 :].startswith("7573746172"):
        compression_format = "split_tar"
        msg = f"{file} is first file of split tar"
        logger.info(msg)
    elif signature.startswith("504b0304"):
        compression_format = "zip"
    elif signature.startswith("425a68"):
        compression_format = "bz2"
    else:
        compression_format = "UNKNOWN"
    return compression_format


def extract_from_string(any_string: str, regex_pattern: str) -> list:
    """Extract all matches from a string using a regex pattern.

    Args:
        any_string: String to search in.
        regex_pattern: Regular expression pattern to use.

    Returns:
        List of all matches found.
    """
    return re.findall(regex_pattern, any_string)


def execute_threaded_function(
    func: Callable,
    args_list: list,
    number_of_threads: int = 8,
) -> list:
    """Execute a function in parallel using multiple threads.

    Args:
        func: The function to be executed.
        args_list: Iterable with arguments to use as input for the function.
        number_of_threads: Number of parallel threads to use.

    Returns:
        List of results returned by the function for each input.

    Raises:
        ValueError: If nesting of args_list elements is inconsistent.
    """

    def _is_nested(arg: str | list | tuple) -> bool:
        return isinstance(arg, list | tuple)

    if len(args_list) == 0:
        msg = f"Can't execute function without args! Args list is {args_list}"
        logger.error(msg)
        results = None
    else:
        first_is_nested = _is_nested(args_list[0])
        if not all(_is_nested(arg) == first_is_nested for arg in args_list):
            msg = "Inconsistent nesting: All elements must be either nested or not nested."
            raise ValueError(msg)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=number_of_threads,
        ) as executor:
            if first_is_nested:
                results = list(executor.map(lambda args: func(*args), args_list))
            else:
                results = list(executor.map(func, args_list))
    return results


def sort_versions(item: str) -> tuple:
    """Sort key for semantic versions with 'latest' appearing first if available.

    Args:
        item: String representing a tool and version (e.g. "foo:1.2.3" or "foo:latest").

    Returns:
        Tuple used for sorting: (tool name, -1 if latest else 0, parsed Version object or None).
    """
    if ":" not in item:
        return (item, 1, None)
    tool, version = item.split(":")
    is_latest = -1 if version == "latest" else 0
    parsed_version = Version(version) if version != "latest" else None
    return (tool, is_latest, parsed_version)


def get_next_port(
    last_assigned_port: int,
    last_port: int,
    is_lastest: bool = False,
) -> int:
    """Get the next assignable port, optionally rounding up to the next 10 for 'latest' tools.

    Args:
        last_assigned_port: Last assigned port number.
        last_port: Highest available port number.
        is_lastest: If True, allocate a port ending with zero for 'latest' tools.

    Returns:
        The next port number to be assigned.

    Raises:
        IndexError: If there are not enough ports available.
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
