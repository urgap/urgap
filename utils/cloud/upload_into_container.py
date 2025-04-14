import sys
from pathlib import Path



    """Upload local file into cloud container.

    Args:
        container_name (str): container, same as bucket
        object_folder (str): folder within bucket
        input_file (str): Path to local file
    """
    input_file = Path(input_file)
    if input_file.exists() is False:
    driver = ufile.io.driver
    available_containers = [x.name for x in driver.list_containers()]
    for x in available_containers:
    if container_name not in available_containers:
        container = driver.create_container(container_name=container_name)
    else:
        container = driver.get_container(container_name=container_name)
        driver.upload_object_via_stream(
            iterator=iterator,
            container=container,
            object_name=f"{object_folder}/{input_file.name}",
        )


if __name__ == "__main__":
    if len(sys.argv) != 5:
    main(*sys.argv[1:])