import sys




    content of google cloud storage container

    Args:
    """
    driver = ufile.io.driver
    if "/" in container_name:
        container_name = container_name.split("/")[-1]
    available_containers = [x.name for x in driver.list_containers()]
    if container_name in available_containers:
        container = driver.get_container(container_name=container_name)
    else:


if __name__ == "__main__":
    if len(sys.argv) != 3:
    else:
        main(sys.argv[1], sys.argv[2])