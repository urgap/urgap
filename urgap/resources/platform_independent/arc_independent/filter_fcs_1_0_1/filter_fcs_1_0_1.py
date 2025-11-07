"""Resource to filter FCS files."""

import argparse
import logging

from pathlib import Path

import flowio
import numpy as np
import pandas as pd


def read_fcs(path: Path) -> tuple[pd.DataFrame, str]:
    """Read FCS file and return the metadata and a sample dataframe.

    Args:
        path (Path): path to FCS file

    Returns:
        df (pd.DataFrame): pandas dataframe with sample data
        metadata (dict): all attributes stored in the FCS header
    """
    fcs_data = flowio.FlowData(path)
    channels = []
    for _k, v in sorted(fcs_data.channels.items(), key=lambda x: int(x[0])):
        channels.append((v.get("PnN", ""), v.get("PnS", "")))
    samples = np.reshape(fcs_data.events, (-1, fcs_data.channel_count))
    metadata = fcs_data.text
    if "filename" in metadata:
        del metadata["filename"]
    fcs_input_df = pd.DataFrame(
        samples,
        columns=pd.MultiIndex.from_tuples(channels, names=["PnN", "PnS"]),
    )

    return fcs_input_df, metadata


def write_fcs(
    output_path: str | Path,
    df: pd.DataFrame,
    metadata: dict | None = None,
) -> None:
    """Write new FCS file.

    Args:
        output_path (Path): path to write new fcs file to
        df (pd.DataFrame): pandas dataframe with sample data
        metadata (dict): all attributes stored in the FCS header
    """
    with output_path.open("wb") as f:
        flowio.create_fcs(
            file_handle=f,
            event_data=df.to_numpy().flatten(),
            channel_names=df.columns.get_level_values("PnN").to_list(),
            opt_channel_names=df.columns.get_level_values("PnS").to_list(),
            metadata_dict=metadata,
        )


def main(
    fcss: str | Path | list | None = None,
    query_string: str | None = None,
    output: str | Path | None = None,
) -> None:
    r"""Filter and merge node.

    Args:
        fcss (list): Path to FCSs (can be multiple)

        query_string (str): pandas df.query style strings.
            Note: It is worth selecting each column by encapsulating it with
            `\ in order to avoid errors, e.g.:
                " -1 < \`Accuracy (ppm)\` < 1 and \`MS-GF:RawScore\` > 10"

        output (Path): Path to output csv file post filtering
    """
    dfs = []
    if len(fcss) > 1:
        metadata = None
        for fcs in fcss:
            if Path(fcs).exists() is True:
                sub_df, sub_metadata = read_fcs(fcs)
                if metadata is None:
                    metadata = sub_metadata
                else:
                    logging.warning("Only using metadata of first FCS file read")
                dfs.append(sub_df)
            else:
                msg = f"FCS file {fcs} does not exist, thus will be skipped!"
                logging.warning(msg)
        input_fcs_df = pd.concat(dfs)
    else:
        input_fcs_df, metadata = read_fcs(fcss[0])
    filtered_df = input_fcs_df.copy()

    try:
        idx = (
            filtered_df.droplevel(
                level=list(range(1, filtered_df.columns.nlevels)),
                axis=1,
            )
            .query(query_string)
            .index
        )
        filtered_df = filtered_df.loc[idx, :]
    except (pd.errors.UndefinedVariableError, SyntaxError, ValueError) as e:
        msg = f"Query string {query_string} is invalid"
        msg += f"Dataframe cols: {input_fcs_df.columns}"
        logging.warning(msg)
        raise RuntimeError from e

    msg = f"Filtered {input_fcs_df.shape[0] - filtered_df.shape[0]} rows"

    logging.info(msg)
    if filtered_df.empty is True:
        logging.warning("All rows have been filtered out!")
    filtered_df = filtered_df.reset_index(drop=True)

    write_fcs(output_path=output, df=filtered_df, metadata=metadata)


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
        fcss=args.input_files,
        output=args.output_file,
        query_string=args.query_string,
    )
