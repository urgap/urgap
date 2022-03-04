import sys


    """Upload local file into cloud container.

    Args:
        container_name (str): container, same as bucket
        input_file (str): Path to local file
            the object name is as_posix().split("/")[-2:]
    """
    input_file = Path(input_file).resolve()
    if input_file.exists() is False:

    input_file = Path(input_file).resolve()
    fragment = "/".join(input_file.as_posix().split("/")[-2:])

    rest = "/".join(input_file.as_posix().split("/")[:-2])
    ufile.rebase(f"{scheme}://{container_name}")
    ufile.upload()


if __name__ == "__main__":
    if len(sys.argv) != 4:
    main(*sys.argv[1:])