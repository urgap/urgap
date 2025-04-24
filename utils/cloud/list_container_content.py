"""Container Content Lister."""

import sys



def main(url: str, container_name: str) -> None:

    content of google cloud storage container

    Args:
        container_name (str): name of container
    """
    driver = ufile.io.driver
    if "/" in container_name:
        container_name = container_name.split("/")[-1]
    available_containers = [x.name for x in driver.list_containers()]
    for _x in available_containers:
        pass
    if container_name in available_containers:
        container = driver.get_container(container_name=container_name)
    else:
        sys.exit(1)
    uri_list = [
        f"{url}/{container_name}#{obj.name}" for obj in container.list_objects()
    ]
    for _uf in uf_list:
        pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        pass
    else:
        main(sys.argv[1], sys.argv[2])