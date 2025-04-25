"""BasicFunction Test Resource v1.3.0."""

import argparse
import logging
import pprint


def main(
    input_files: str | None = None,
    output_files: str | None = None,
    params: str | None = None,
) -> str:
    """Write Test file v1.3.0.

    Args:
        input_files (str, optional): dOooo. Defaults to None.
        output_files (str, optional): Where to write the dummy content in. Defaults to None.
        params (str, optional): doOOoo. Defaults to None.

    Returns:
        str: Test String
    """
    if output_files is not None:
        for output_file in output_files:
                print(params, file=oo)
                print(input_files, file=oo)
                print(main.__doc__, file=oo)
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