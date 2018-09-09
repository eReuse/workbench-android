import subprocess


def get_data_partition(_sn):
    """Get data partiton.
    Args:
        _sn (str): Serial number.
    Returns:
        str: Partition path.
        """

    command = 'adb -s {serial_number} shell mount' \
        .format(serial_number=_sn)

    p = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    while True:
        sn_line = p.stdout.readline()
        if not sn_line:
            break

        if '/data' in sn_line:
            return sn_line.split()[0]


def erase_partition(partition, _sn):
    """Get data partiton.
    Args:
        _sn (str): Serial number.
    Returns:
        str: Partition path.
        """

    command_first = 'adb -s {serial_number}' \
        .format(serial_number=_sn)

    command_end = 'shell dd if=/dev/zero of={partition}' \
        .format(partition=partition)

    p = subprocess.Popen(
        command_first.split() + command_end.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )


if __name__ == '__main__':
    serial_number = "21f4c3ce"
    partition = get_data_partition(serial_number)
    erased = erase_partition(partition, serial_number)
