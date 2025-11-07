"""Test Node Code."""

import argparse

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    """Test node function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", dest="output_files", nargs="+")
    known_args = parser.parse_args(argv)

    hal = "Dave, this conversation can serve no purpose anymore. Goodbye."
    for file in known_args.output_files:
        with file.open("w") as oo:
            print(hal, file=oo)


if __name__ == "__main__":
    main()
