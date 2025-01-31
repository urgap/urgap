"""Compressor resource."""

import argparse
import logging
import os.path
import subprocess
import tarfile

from ast import literal_eval
from pathlib import Path
from zipfile import ZipFile


def main(
    compression_format: str,
    file_list: list,
    output_file_path: str,
    """Create tar or zip archive from input file list.

    Selecting split_tar splits tar archive into parts.

    Args:
        compression_format: Currently supported are tar, zip and split_tar.
        file_list (list): list of tuples of file Path objects and tag Path objects (or None).
        output_file_path (Path): path object for output.
    """
    if max_tar_size is not None:
        files_to_archive = [files[0] for files in file_list]
        common_base = Path(os.path.commonpath(files_to_archive)).parent
        relative_files = [Path(f).relative_to(common_base) for f in files_to_archive]
        tar_process = subprocess.Popen(
            stdout=subprocess.PIPE,
        )
        split_process = subprocess.Popen(
            [
                "split",
                "-b",
                "-",
                f"{Path(output_file_path).parent / 'part.'}",
            ],
            stdin=tar_process.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        tar_process.stdout.close()
        split_process.communicate()
        tar_process.wait()
        if tar_process.returncode != 0:
        if split_process.returncode != 0:
        else:
    elif compression_format == "tar":
        with tarfile.open(output_file_path, mode="w:") as tar:
            for file, tag in file_list:
                tar.add(file, arcname=Path(file).name)
    elif compression_format == "zip":
            for file, tag in file_list:
                if tag is not None:
    else:


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_files",
        dest="input_files",
        action="append",
        help="input files to be compressed",
    )
    parser.add_argument("-o", "--output_file", dest="output_file", help="output file")
    parser.add_argument(
        "-cf",
        "--compression_format",
        dest="compression_format",
        help="compression format: tar or zip",
    )
    parser.add_argument(
        "-s",
        "--size",
        dest="max_tar_size",
    )
    args = parser.parse_args()

    main(
        file_list=[literal_eval(str_tuple) for str_tuple in args.input_files],
        output_file_path=args.output_file,
        compression_format=args.compression_format,
        max_tar_size=args.max_tar_size,
    )