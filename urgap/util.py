
import binascii
import logging
import os



def sense_compression_format(file: os.PathLike) -> str:


    Args:

    Returns:
    """
    if signature.startswith("1f8b"):
    elif signature[257 * 2 :].startswith("7573746172"):
    elif signature.startswith("504b0304"):
    elif signature.startswith("425a68"):
    else:

