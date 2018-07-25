import json
import os
import time
import logging
import conf_log
from workbench_android import workbench_android


DEBUG_LEVEL = logging.DEBUG
DATA_FOLDER = os.path.join(os.getcwd(), 'devices_data')


def bootloader_flash():
    """Flash device"""
    while not wba.devices_on_bootload():
        logger.warning(
            'Please, reboot device/s to bootloader.\n'
            'Press enter to try again or type \'s\' or \'Skip\' to continue.'
        )
        if input().lower().startswith("s"):
            break

        wba.set_bootloader()  # Help for the user to set them on bootloader.

    else:

        while wba.devices_on_bootload():
            flashed = wba.flash_device()
            logger.debug(
                'Last results == {}\n'
                'Waiting 1 second before to retry.'.format(flashed)
            )
            time.sleep(1)
        else:
            logger.info('All devices has been flashed.')


def get_devices_information():
    """Get information for every device connected on ADB.

    Creates a folder on r'.' called `devices_data`.

    """
    devices = wba.list_devices()
    while not devices:
        logger.warning(
            'Devices not detected.\n'
            'Press enter to try again or type \'s\' or \'Skip\' to continue.'
        )
        if input().lower().startswith("s"):
            exit(1)

        devices = wba.list_devices()

    for _serial_number in devices:
        yield _serial_number, wba.export(_serial_number)


if __name__ == '__main__':
    conf_log.configure(DEBUG_LEVEL)
    logger = logging.getLogger("Workbench-android")

    # Workbench-Android call.
    wba = workbench_android.WorkbenchAndroid()

    # 1. boot to bootloader (usually manually touching buttons)
    wba.set_bootloader()

    # @TODO: 2. get device info through usb protocol.

    # 3. execute `heimdall` or similar depending of usb.idVendor X
    bootloader_flash()

    # 4. Enter into recovery.
    wba.set_recovery()

    # 5. Get device information.
    for serial_number, export in get_devices_information():

        file_path = os.path.join(DATA_FOLDER, '{}.json'.format(serial_number))
        if not os.path.exists(DATA_FOLDER):
            os.mkdir(DATA_FOLDER)

        with open(file_path, 'w') as _file:
            json.dump(export, _file,  indent=4, sort_keys=True)

    # 6. wipe

    # 7. install custom OS
    # have fun!
