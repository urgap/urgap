"""Filter / and or merge files with polars operations."""

import argparse
import logging
import pprint
import zipfile

from pathlib import Path

import polars as pl

logger = logging.getLogger(__name__)


def sense_file_format(file: str) -> str:
    """Sense the format of a file.

    Args:
        file: File to analyze.

    Returns:
        File format as string.
    """
    with Path(file).open("rb") as f:
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


def read_lazy_frames(grouped_input_files: dict, sep: str) -> list:
    """Read all files lazily where possible. Eagerly read xlsx and convert to LazyFrame.

    Args:
        grouped_input_files: Input files split up in corresponding lists.
        sep: separator for csv files.

    Returns:
        lazy_frames: List of LazyFrames
    """
    lazy_frames = [
        pl.scan_csv(csv_file, separator=sep)
        for csv_file in grouped_input_files.get("csv", [])
    ]
    lazy_frames.extend(
        [
            pl.scan_parquet(parquet_file)
            for parquet_file in grouped_input_files.get("parquet", [])
    )
    for xlsx_file in grouped_input_files.get("xlsx", []):
        xlsx_frame = pl.read_excel(xlsx_file)
        lazy_frames.append(xlsx_frame.lazy())
    return lazy_frames


def write_dfs(df: pl.DataFrame, mode: str, output: str) -> None:
    """Write any of the CSV, Parquet and XLSX files using polars.

    Args:
        df: The DataFrame to write to disk.
        mode: Output file format ('csv', 'parquet', or 'xlsx').
        output: Path to the output file.

    Returns:
        None
    """
    if mode == "csv":
        df.write_csv(output)
    elif mode == "parquet":
        df.write_parquet(output)
    elif mode == "xlsx":
        df.write_excel(output)
    else:
        msg = (
            f"Filter mode has to be defined with -m. "
            f"You defined filter mode {mode} which is currently not supported. "
            f"Supported modes are 'csv', 'parquet' and 'xlsx'."
        )
        raise ValueError(msg)


def main(
    input_files: str | Path | list | None = None,
    query_string: str | None = None,
    output: str | None = None,
    mode: str | None = None,
    sep: str | None = None,
) -> None:
    """Filter and merge node using polars.

    Args:
        input_files: List of input file paths or None.
        query_string: SQL WHERE clause for filtering rows, or None.
        output: Path to the output file.
        mode: Output file format ('csv', 'parquet', or 'xlsx').
        sep: Separator for CSV files (default is ',').

    Returns:
        None
    """
    if len(input_files) == 0:
        msg = "I need input files!..."
        raise OSError(msg)

    grouped_input_files = get_input_file_lists(input_files)
    logger.info(pprint.pformat(grouped_input_files))
    lazy_frames = read_lazy_frames(grouped_input_files, sep)
    if not lazy_frames:
        logger.warning("No input files to process!")
        return
    merged_df = merged_lazy.collect()
    if query_string is not None:
        try:
            filtered_df = merged_df.sql(f"SELECT * FROM self WHERE {query_string}")
            merged_df = filtered_df
        except Exception as e:
            msg = f"Query string {query_string} is invalid"
            logger.warning(msg)
            raise RuntimeError(msg) from e
    if merged_df.is_empty():
        logger.warning("All rows have been filtered out!")
    write_dfs(merged_df, mode=mode, output=output)


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
        help="polars filter expression as a string",
    )
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        help="filter mode like csv or parquet",
    )
    parser.add_argument(
        "-s",
        "--sep",
        dest="sep",
        default=",",
        help="Seperator or delimiter. Defaults to ','",
    )
    args = parser.parse_args()
    main(
        input_files=args.input_files,
        output=args.output_file,
        query_string=args.query_string,
        mode=args.mode,
        sep=args.sep,
    )