"""Container Uploader."""

import sys

from pathlib import Path

import urgap


def main(scheme: str, container_name: str, input_file: str) -> None:
    """Upload local file into cloud container.

    Args:
        container_name (str): container, same as bucket
        input_file (str): Path to local file
            the object name is as_posix().split("/")[-2:]
    """
    input_file = Path(input_file).resolve()
    if input_file.exists() is False:
        msg = "Local file does not exist!"
        raise OSError(msg)

    input_file = Path(input_file).resolve()
    fragment = "/".join(input_file.as_posix().split("/")[-2:])

    rest = "/".join(input_file.as_posix().split("/")[:-2])
    ufile = urgap.UFile(uri=f"file://{rest}#{fragment}")
    ufile.rebase(f"{scheme}://{container_name}")
    ufile.upload()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(1)
    main(*sys.argv[1:])