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


def get_input_file_lists(input_files: list) -> dict:
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


def read_dfs(grouped_input_files: dict, sep: str | None) -> list:
    """Read any of the CSV, Parquet and XLSX files.

    Args:
        sep: Seperator or delimiter for read csv function.

    Returns:
    """
    pd_functions = {
        "csv": {"function": pd.read_csv},
        "parquet": {"function": pd.read_parquet},
        "xlsx": {"function": pd.read_excel},
    }
    dfs = []
    for file_type, file_list in grouped_input_files.items():
        if file_type == "csv":
            dfs.extend(
            )
        else:
            dfs.extend(pd_functions[file_type]["function"](file) for file in file_list)
    return dfs


def write_dfs(df: pd.DataFrame, mode: str, output: str) -> None:
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
        msg = (
            f"Filter mode has to be defined with -m."
            f"You defined filter mode {mode} which is currently not supported."
            f"Supported modes are 'csv', 'parquet' and 'xlsx'."
        )
        raise ValueError(msg)


def merge_parquet_files(grouped_input_files: dict, output_file_path: str) -> None:
    """Merge all parquet files and write to the destination file path.

    Args:
        grouped_input_files: Input grouped_input_files.
        output_file_path: Output parquet file path.

    Returns:
        True when successful else False.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    parquet_files = grouped_input_files["parquet"]
    with pq.ParquetWriter(
    ) as writer:
        for parquet in parquet_files:
            if Path(parquet).exists() is False:
                msg = f"Parquet file {parquet} does not exist!"
                raise FileNotFoundError(msg)
            pf = pq.ParquetFile(parquet)

            for batch in pf.iter_batches(batch_size=6553600):
                table = pa.Table.from_batches([batch])
                writer.write_table(table)


def main(
    input_files: str | Path | list | None = None,
    query_string: str | None = None,
    output: str | None = None,
    mode: str | None = None,
    sep: str | None = None,
) -> None:
    r"""Filter and merge node.

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
        msg = "I need input files!..."
        raise OSError(msg)

    grouped_input_files = get_input_file_lists(input_files)
    if (
        mode == "parquet"
        and len(grouped_input_files.get("csv", [])) == 0
        and len(grouped_input_files.get("parquet", [])) > 1
        and len(grouped_input_files.get("xlsx", [])) == 0
        and query_string is None
    ):
        merge_parquet_files(grouped_input_files, output)

    else:
        dfs = read_dfs(grouped_input_files, sep)
        concatenated_df = pd.concat(dfs)
        if query_string is not None:
            old_len = len(concatenated_df)
            try:
                concatenated_df = concatenated_df.query(query_string)
                msg = f"Query string {query_string} is invalid"

            msg = f"Filtered {old_len - concatenated_df.shape[0]} rows"

        if concatenated_df.empty is True:
        concatenated_df = concatenated_df.reset_index(drop=True)
        write_dfs(concatenated_df, mode=mode, output=output)


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