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
    files = {"csv": [], "parquet": [], "xlsx": []}
    for file in input_files:
        input_file_type = sense_file_format(file)
        files[input_file_type].append(file)
    return files


    """Read any of the CSV, Parquet and XLSX files.

    Args:

    Returns:
    """
    pd_functions = {
        "csv": {"function": pd.read_csv},
        "parquet": {"function": pd.read_parquet},
        "xlsx": {"function": pd.read_excel},
    }
    dfs = []
    for file_type, file_list in grouped_input_files.items():
    return dfs


    """Write any of the CSV, Parquet and XLSX files.

    Args:

    Raises:
    """
    if mode == "csv":
        df.to_csv(output, index=False)
    elif mode == "parquet":
        df.to_parquet(output, index=False)
    elif mode == "xlsx":
        df.to_excel(output, index=False)
    else:
            f"Filter mode has to be defined with -m."
            f"You defined filter mode {mode} which is currently not supported."
            f"Supported modes are 'csv', 'parquet' and 'xlsx'."
        )


def merge_parquet_files(grouped_input_files: dict, output_file_path: str) -> None:
    """Merge all parquet files and write to the destination file path.

    Args:
        output_file_path: Output parquet file path.

    Returns:
        True when successful else False.
    """
    import pyarrow as pa

    parquet_files = grouped_input_files["parquet"]
    with pq.ParquetWriter(
    ) as writer:
        for parquet in parquet_files:
            if Path(parquet).exists() is False:
            pf = pq.ParquetFile(parquet)

            for batch in pf.iter_batches(batch_size=6553600):
                table = pa.Table.from_batches([batch])
                writer.write_table(table)


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
    if len(input_files) == 0:

    grouped_input_files = get_input_file_lists(input_files)
    if (
        mode == "parquet"
        and query_string is None
    ):

    else:
        if query_string is not None:
            try:



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