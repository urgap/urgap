"""Test Node Code."""

import argparse
from pathlib import Path


def main(
    input_files: list | None = None,
    output_files: list | None = None,
    params: str | list | None = None,
) -> str:
    """Test node function."""
    if output_files is not None:
        for output_file in output_files:
            with Path(output_file).open("w") as oo:
                print(params, file=oo)
                print(input_files, file=oo)
    return "I am a yummy test dummy!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input_files", nargs="+")
    parser.add_argument("--output", dest="output_files", nargs="+")
    parser.add_argument(
        "--params",
        dest="params",
    )
    args = parser.parse_args()
    main(
        input_files=args.input_files,
        output_files=args.output_files,
        params=args.params,
    )