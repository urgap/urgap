"""Filter / and or merge csv files.

usage:
    csv_filter.py <csv_1> <csv_2> ...

"""

import argparse
import logging

from pathlib import Path

import pandas as pd


def main(
    csvs: str | list | None = None,
    query_string: str | None = None,
    output: str | None = None,
) -> None:
    r"""Filter and merge node.

    Args:
        csvs (str): Path to csv (can be multiple)

        query_string (str): pandas df.query style strings.
            Note: It is worth selecting each column by encapsulating it with
            `\ in order to avoid errors, e.g.:
                " -1 < \`Accuracy (ppm)\` < 1 and \`MS-GF:RawScore\` > 10"

        output (str): Path to output csv file post filtering
    """
    dfs = []
    if len(csvs) > 1:
        for csv in csvs:
            if Path(csv).exists() is True:
                dfs.append(pd.read_csv(csv))
            else:
                msg = f"CSV file {csv} does not exist, thus will be skipped!"
                logging.warning(msg)
        csv_input_df = pd.concat(dfs)
    else:
        csv_input_df = pd.read_csv(csvs[0])
    filtered_df = csv_input_df.copy()

    try:
        filtered_df = filtered_df.query(query_string)
    except (pd.errors.UndefinedVariableError, SyntaxError, ValueError) as e:
        msg = f"Query string {query_string} is invalid"
        msg += f"Dataframe cols: {csv_input_df.columns}"
        logging.warning(msg)
        raise RuntimeError(msg) from e

    msg = f"Filtered {csv_input_df.shape[0] - filtered_df.shape[0]} rows"
    logging.info(msg)
    if filtered_df.empty is True:
        logging.warning("All rows have been filtered out!")
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.to_csv(output, index=False)


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
    args = parser.parse_args()

    main(
        csvs=args.input_files,
        output=args.output_file,
        query_string=args.query_string,
    )
