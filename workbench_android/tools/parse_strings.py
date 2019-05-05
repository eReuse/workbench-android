def get_partitions(mount_string: str) -> dict:
    """
    Parses the output of `mount` command and return a dictionary with
    the mount point as key and block path has value.

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


def get_devices(string) -> dict:
    devices = {}
    for line in string.split('\n'):
        if line == '':
            continue

        serial, status, *_ = line.split()

        if len(serial) != 8:
            continue

        devices[serial] = status

    return devices


def simple_string(string: str) -> str:
    """
    Just strips \n characters.

    :param str string:
    :return: The string parsed.
    """
    return string.strip()


def uptime(string):
    """
    Parses the output of `cat /proc/uptime`.

    :param str string:
    :return: Parsed tuple ints.
    """
    return [float(value) for value in string.strip().split()]
