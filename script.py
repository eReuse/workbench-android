import time
import logging
import conf_log
from workbench_android import workbench_android

conf_log.configure(logging.DEBUG)


# 4. enter into recovery (can this be auto?)
# 5. when in recovery, execute the following:

logger = logging.getLogger("Workbench-android")

# Workbench-Android call.
wba = workbench_android.WorkbenchAndroid()

# Search for all device detected and reboot them to fastboot mode.

# 1. boot to bootloader (usually manually touching buttons)
while not wba.devices_on_bootload():
    logger.warning(
        'Please, reboot device/s to bootloader.\n'
        'Press enter to try again or type \'s\' or \'Skip\' to continue.'
    )
    if input().lower().startswith("s"):
        break

    wba.set_bootloader()  # Help for the user to set them on bootloader.

else:
    # @TODO: 2. get device info through usb protocol.

    # 3. execute heimdall or similar depending of usb.idVendor X
    while wba.devices_on_bootload():
        flashed = wba.flash_device()
        logger.debug(
            'Last results == {}\n'
            'Waiting 1 second before to retry.'.format(flashed)
        )
        time.sleep(1)
    else:
        logger.info('All devices has been flashed.')

devices = wba.list_devices()
while not devices:
    logger.warning(
        'Devices not detected.\n'
        'Press enter to try again or type \'s\' or \'Skip\' to continue.'
    )
    if input().lower().startswith("s"):
        exit(1)

    devices = wba.list_devices()

for device in devices:
    wba.connect_device(device)
    logger.info(
        'Device {}: Model {}.'.format(
            device, wba.get_model(device)
        )
    )

# print(device.Shell('getprop'))
# print(device.Shell('getprop ro.product.model'))

# model = device.Shell('getprop ro.product.model').strip()

#    and usb.idProduct Y, flashing the recovery
# get device data
# serial number, model, mnaufacturer
# can we get imei / meid?
# can we get battery status?
# android version

# print(device.Shell('getprop'))
# print(device.Shell('getprop ro.product.model'))

# 6. wipe
# 7. install custom OS
# have fun!
