"""Upload into Container."""

import logging
import sys

from pathlib import Path



def main(scheme: str, container_name: str, object_folder: str, input_file: str) -> None:
    """Upload local file into cloud container.

    Args:
        container_name (str): container, same as bucket
        object_folder (str): folder within bucket
        input_file (str): Path to local file
    """
    input_file = Path(input_file)
    if input_file.exists() is False:
        msg = "Local file does not exist!"
        raise OSError(msg)
    driver = ufile.io.driver
    available_containers = [x.name for x in driver.list_containers()]
    logging.info("Available containers:")
    for x in available_containers:
        msg = f" - {x}"
        logging.info(msg)
    if container_name not in available_containers:
        container = driver.create_container(container_name=container_name)
        msg = f"Creating container {container_name}"
        logging.info(msg)
    else:
        container = driver.get_container(container_name=container_name)
        driver.upload_object_via_stream(
            iterator=iterator,
            container=container,
            object_name=f"{object_folder}/{input_file.name}",
        )


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(1)
    main(*sys.argv[1:])