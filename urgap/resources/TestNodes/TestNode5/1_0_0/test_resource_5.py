"""Test Node Code."""

import argparse

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> str:
    """Test node function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="input_files", nargs="+")
    parser.add_argument("--output", dest="output_files", nargs="+")
    parser.add_argument(
        "--params",
        dest="params",
    )
    known_args = parser.parse_args(argv)

    for file in known_args.output_files:
            print(known_args.params, file=oo)
    return "Mischief Managed."


if __name__ == "__main__":
    main()