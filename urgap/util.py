
import binascii
import concurrent.futures
import logging
import os
import re



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