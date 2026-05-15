"""pymzml resource."""

import logging
import sys

from pathlib import Path

from pymzml.run import Reader
from pymzml.utils.utils import index_gzip


def main(
    mzml: str | Path | None = None,
    idxgz: str | Path | None = None,
) -> None:
    """Convert mzML to idxgz.

    A new .idxgz file will be created at the specified location

    Usage:
    ./pymzml2idxgz.py <mzML_file_name> <idxgz_file_name>

    Args:
        mzml (str, Path): path to mzml file
        idxgz (str, Path): path to idxgz file
        **kwargs: further kwargs

    Returns:
        idxgz (str): output file path
    """
    logging.info("Converting file:\n\tmzml : %s\n\tto\n\tidxgz : %s", mzml, idxgz)
    with Path.open(mzml) as fin:
        fin.seek(0, 2)
        max_offset_len = fin.tell()
        max_spec_no = Reader(mzml).get_spectrum_count() + 10

    index_gzip(mzml, idxgz, max_idx=max_spec_no, idx_len=len(str(max_offset_len)))

    logging.info("Zipped mzML to location %s", idxgz)
    return idxgz


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        raise RuntimeError
    else:
        main(mzml=sys.argv[1], idxgz=sys.argv[2])
