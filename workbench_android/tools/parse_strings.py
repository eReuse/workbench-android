def get_partitions(mount_string: str) -> dict:
    """
    Parses the output of `mount` command and return a dictionary with
    the mountpoint as key and block path has value.

    :param mount_string:
    :return:
    """
    partitions = dict()
    for line in mount_string.split('\n'):
        if len(line.split()) < 3:
            continue

        device, is_on, point, *_ = line.split()
        if 'on' == is_on:
            partitions[point] = device

    return partitions
