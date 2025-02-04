"""Filter / and or merge files with pandas operations."""

import argparse
import logging
import zipfile
from pathlib import Path

import pandas as pd


def sense_file_format(file: str) -> str:
    """Sense the format of a file.

    Args:
        file: File to analyze.

    Returns:
        File format as string.
    """
        match f.read(4):
            case b"PAR1":
                f.seek(-4, 2)
                if f.read(4) == b"PAR1":
                    return "parquet"
            case b"PK\x03\x04":
                with zipfile.ZipFile(file, "r") as zip_file:
                    required_files = ["[Content_Types].xml", "xl/"]
                    if any(file in zip_file.namelist() for file in required_files):
                        return "xlsx"
        return "csv"


    """Get the separate input file lists for csv, parquet and xlsx.

    Args:
        input_files: All input files.

    Returns:
        Input files split up in corresponding lists.
    """
    for file in input_files:
        input_file_type = sense_file_format(file)



    Args:

    Returns:
    """



    Args:

    """


def main(

    Args:
        sep: Seperator or delimiter. Defaults to ','
        mode: Defines the output file type.
        input_files: Path to files (can be multiple).

        query_string (str): pandas df.query style strings.
            Note: It is worth selecting each column by encapsulating it with
            `\ in order to avoid errors, e.g.:
                " -1 < \`Accuracy (ppm)\` < 1 and \`MS-GF:RawScore\` > 10"

        output (str): Path to output file post filtering.
    """
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
        "-q",
        "--query_string",
        dest="query_string",
        help="pandas query string",
    )
    parser.add_argument(
    )
    parser.add_argument(
    )
    args = parser.parse_args()
    main(
        input_files=args.input_files,
        output=args.output_file,
        query_string=args.query_string,
        mode=args.mode,
        sep=args.sep,
    )