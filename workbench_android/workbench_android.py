import time
import logging
import os.path as op
import subprocess
import traceback
from adb import adb_commands
from adb import sign_m2crypto
from usb1 import USBError


class WorkbenchAndroid:
    """
    Manages `heimdall` and `adb` to flash and securely
    erase personal data.
    """

    def __init__(self, target=None):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.adb = adb_commands.AdbCommands()
        self._signer = sign_m2crypto.M2CryptoSigner(
            op.expanduser('~/.android/adbkey')
        )

    @staticmethod
    def devices_on_bootload():
        """Connect ot the device.

        Returns:
            bool: True if any device is detected.
        """
        return bool(subprocess.run(('heimdall', 'detect')).returncode == 0)

    @staticmethod
    def flash_device():
        """Connect ot the device.

        Returns:
            bool: True if any device is detected.
        """
        try:
            return bool(
                subprocess.run(
                    ('heimdall', 'flash', '--RECOVERY', 'recovery.img')
                ).returncode == 0
            )

        except Exception:
            traceback.print_last()  # Show the exception on terminal.
            return False

    def list_devices(self):
        """Connect ot the device.

        Returns:
            dict: Dictionary with device serial numbers as str.
        """
        return [x.serial_number for x in self.adb.Devices()]

    def set_bootloader(self):
        """Set bootloader for all current devices."""
        for serial_number in self.list_devices():
            self.connect_device(serial_number)
            self.adb.RebootBootloader()
            self.adb.Close()

    def set_recovery(self):
        """Reboot all devices detected into Recovery mode."""
        for serial_number in self.list_devices():
            self.connect_device(serial_number)
            self.adb.RebootBootloader()
            self.adb.Close()

    def export(self, serial_number):
        """Export device information of given `serial_number`.

        print(device.Shell('getprop'))
        print(device.Shell('getprop ro.product.model'))

        model = device.Shell('getprop ro.product.model').strip()

           and usb.idProduct Y, flashing the recovery
        get device data
        serial number, model, mnaufacturer
        can we get imei / meid?
        can we get battery status?
        android version

        print(device.Shell('getprop'))
        print(device.Shell('getprop ro.product.model'))
        Args:
            serial_number (str): Serial number of the device.
        """
        outputs = self.shell(
            [
                'getprop ro.product.model',
                'getprop ro.product.brand',
            ],
            target=serial_number
        )
        return dict(
            model=outputs[0],
            brand=outputs[1],
        )

    def shell(self, command, target=None):
        """Automatically start a communication with the device serial number.

        Args:
            command (str or list): A command or a list of commands to
                execute on the device shell.
            target (str): The serial number of the device.
        Returns:
            str or list: A string with the output or a list of strings
                with the output of all commands.
        """
        self.adb.ConnectDevice(serial=target.encode('UTF-8'))

        if isinstance(command, str):
            output = self.adb.Shell(command).strip()
        elif isinstance(command, list):
            output = [self.adb.Shell(execute).strip() for execute in command]
        else:
            raise NotImplementedError(
                'You should send a `str` or `list` command/s.'
            )

        self.adb.Close()

        return output

    def connect_device(self, serial_number, kill_retry=True):
        """Connect ot the device.

        Args:
            serial_number (str): Serial n
            mber of the device.
            kill_retry (bool): If failed with `USBError` exception, try
                to kill-server from adb Linux shell.

        Raises:
            DeviceNotFoundError: When the device is not found.
        """
        try:
            self.adb.ConnectDevice(
                rsa_keys=[self._signer],
                serial=serial_number.encode('UTF-8')
            )

        except USBError as err:
            if kill_retry:
                self.logger.info('Trying to killing the adb server...')
                subprocess.run(('adb', 'kill-server'))
                time.sleep(1)
                self.connect_device(serial_number, kill_retry=False)
            else:
                raise err

    def get_all(self, serial_number):
        """Get all information from `getprop`.

        Returns:
            str: All properties.
        """
        return self.shell('getprop', target=serial_number)

    def get_model(self, serial_number):
        """Get Model name of the device.

        Args:
            serial_number (str): Serial number of the device.

        Returns:
            str: Model name.
        """
        return self.shell('getprop ro.product.model', target=serial_number)
