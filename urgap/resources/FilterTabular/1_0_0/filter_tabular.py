"""Filter / and or merge files with pandas operations."""

import argparse
import logging
from pathlib import Path

import pandas as pd



    Args:

    """


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
    args = parser.parse_args()
    main(
        input_files=args.input_files,
        output=args.output_file,
        query_string=args.query_string,
        mode=args.mode,
    )