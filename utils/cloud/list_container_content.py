"""Container Content Lister."""

import sys

import urgap


def main(url: str, container_name: str) -> None:
    """List object in cloud storage container.

    Using urgap credentials and ufile functionality to list
    content of google cloud storage container

    Args:
        url (str): schema+netloc can be gcs or minio-libcloud
            (need host eg.g hdbsalx091:9010/urgap_dev)
        container_name (str): name of container
    """
    ufile = urgap.UFile(f"{url}/{container_name}/#might_not_even_exists/not_sure.txt")
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
    uf_list = urgap.UFileList.from_uri_list(uri_list)
    for _uf in uf_list:
        pass


if __name__ == "__main__":
    if len(sys.argv) != 3:
        pass
    else:
        main(sys.argv[1], sys.argv[2])
