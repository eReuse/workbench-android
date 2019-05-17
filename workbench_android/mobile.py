import json
import time
import pathlib
import logging
import datetime
import threading
import subprocess

from enum import Enum
from typing import Set, Tuple, Union, List, Dict
from contextlib import suppress

import ereuse_utils

from ereuse_utils import cmd
from ereuse_utils.naming import Naming

from workbench_android.tools import parse_strings
from workbench_android.progressive_cmd import ProgressiveCmd


class ImageNotFoundException(Exception):
    """ Can not found the image on the module resource folder. """


class DeviceNotConnectedException(Exception):
    """ Raised when device has ben not found. """


class ErasureFailedException(Exception):
    """ When a erasure step has been failed. """


class State(Enum):
    UNAUTHORIZED = 'unauthorized'
    DEFAULT = 'device'
    RECOVERY = 'recovery'
    # noinspection SpellCheckingInspection
    FLASH = 'bootloader'
    DISCONNECTED = 'off'


class LongState(Enum):
    Recovery = 'In recovery'
    Erasing = 'Erasing'
    # noinspection SpellCheckingInspection
    WaitingSideload = 'Go to sideload'
    InstallingOS = 'Installing the OS'
    # noinspection SpellCheckingInspection
    WaitSideloadAgain = 'Installed. Relaunch sideload to install Google Apps.'
    # noinspection SpellCheckingInspection
    InstallingGapps = 'Installing the Google Apps'
    BootingIntoOS = 'Booting into OS... don\'t disconnect.'
    Done = 'Done. Check everything works well.'


class Mobile(threading.Thread):
    _mobiles = set()  # type: Set[Mobile]

    def __init__(self, serial_number: str, res: pathlib.Path,
                 jsons: pathlib.Path, handlers: List[logging.Handler] = None):
        # Set the serial number.
        self.serial_number = serial_number

        # Define the default commands.
        self.adb = 'adb', '-s', self.serial_number
        self.shell = *self.adb, 'shell'
        self.getprop = *self.shell, 'getprop'
        # noinspection SpellCheckingInspection
        self.flash = 'heimdall'

        # Default variables
        self.events = []
        self.closed = False

        # Create a logger.
        self.logger = logging.getLogger('{}-{}'.format(
            self.__class__.__name__, self.serial_number))
        self.logger.handlers = handlers or self.logger.handlers
        self.logger.setLevel(logging.DEBUG)

        # Initiate Thread class.
        super().__init__(daemon=True)
        self._thread_event = threading.Event()

        # Check if device is connected.
        if not self.is_available(timeout=60):
            raise DeviceNotConnectedException(self.serial_number)

        # Get properties.
        # noinspection SpellCheckingInspection
        self.imei = None
        self.model = self.get_model()
        self.manufacturer = self.get_manufacturer()
        hid = Naming.hid(
            'Smartphone', self.manufacturer, self.model, self.serial_number)
        self.json_path = jsons / (hid + '.json')

        # self._state_iter = iter(LongState)
        # self._state = next(self._state_iter)
        self._progress = None  # type: Union[ProgressiveCmd, None]
        self._error = None
        self._resources = res / self.model

    def is_available(self, timeout=120):
        start_time = time.time()

        auth_spam = 30  # Spam the message every 30 seconds.
        auth_quiet = 0
        while time.time() < start_time + timeout:
            if self.state() in [State.DEFAULT, State.RECOVERY]:
                return True

            elif auth_spam == auth_spam:
                self.get_auth()
                auth_quiet = 0

            else:
                auth_quiet += 1

            time.sleep(1)

        return False

    def wait_for(self, status):
        """
        Waits to be in the State.

        :param State status: State enum.
        :return: Returns the return code of the command.
        :rtype: int

        """
        self.logger.debug('Waiting for state \'{}\'.'.format(status.value))
        try:
            if status == State.FLASH:
                proc = self._heimdall_detect()

            else:
                proc = cmd.run(*self.adb, 'wait-for-{}'.format(status.value))

        except subprocess.CalledProcessError:
            pass

        self.logger.debug('Device found in state {}.'.format(status.value))
        return proc.returncode

    def _heimdall_detect(self):
        """
        Detect if heimdall find any device.

        This must be in a separated class for Samsung mobiles.
        :return:
        """
        return cmd.run(*self.flash, 'print-pit', '--no-reboot')

    def get_auth(self):
        """
        Resent the authorization prompt to the device.

        :return: Returns True if accepted.
        :rtype: bool
        """
        cmd.run(*self.adb, 'reconnect', 'offline')

    def state(self):
        """
        Returns the current phone status.

        :return: The current status of the phone.
        :rtype: State
        """
        proc = cmd.run(*self.adb, 'get-state', check=False)

        if proc.returncode != 0:
            # Todo: Detect if is Unauthorized or disconnected.
            self.logger.debug('Device not detected or unauthorized.')
            return State.DISCONNECTED

        return State(proc.stdout.strip())

    def current_step(self) -> Tuple[LongState, Union[int, None],
                                    Union[str, None]]:
        """
        Returns information of the process of this mobile.

        Returns the state and, if the state is a progress,
        the number steps performed from the last time this method
        was executed.
        """
        return self._state, self._progress.increment() \
            if self._progress else None, self._error

    def run(self):
        try:
            self._run()
        except subprocess.CalledProcessError as e:
            self._error = '{}: {}'.format(e, e.stderr)

    def _run(self):
        """Processes the device, erasing it, installing the OS, etc."""
        self.next_state()  # Erase step.

        self.set_state(State.RECOVERY)
        self.erase_data_partition()

        self.next_state()  # Flash OS.
        self.install_os()
        self.set_state(State.FLASH)

        self.next_state()  # Installing OS
        start = datetime.datetime.now(datetime.timezone.utc)
        os = 'samsung.zip'
        self._progress = ProgressiveCmd(*self.adb, 'sideload',
                                        self._resources / os,
                                        stdout=subprocess.PIPE,
                                        number_chars=2,
                                        read=10)
        self._progress.run()
        self.events.append({
            'name': os,
            'type': 'Install',
            'elapsed': datetime.datetime.now(datetime.timezone.utc) - start,
            'error': False
        })

        self.next_state()
        self.set_state(State.RECOVERY)

        self.next_state()  # Installing gapps
        self._progress = ProgressiveCmd(*self.adb, 'sideload',
                                        self._resources / 'gapps.zip',
                                        stdout=subprocess.PIPE,
                                        number_chars=2,
                                        read=10)
        self._progress.run()

        self.set_state(State.RECOVERY)
        self.next_state()  # Booting into OS
        cmd.run(*self.adb, 'reboot')
        self.set_state(State.RECOVERY)
        self.save_json()
        self.set_state(State.DEFAULT)  # Default? OS installation will start
        # get imei from https://android.stackexchange.com/a/194514
        # only works when main OS is already booting
        self.imei = cmd.run(
            *self.adb, 'shell', 'service', 'call', 'iphonesubinfo', 1, '|',
            'toybox', 'cut', '-d', "'", '-f2', '|', 'toybox', 'grep', '-Eo',
            "'[0-9]'", '|', 'toybox', 'xargs', '|', 'toybox', 'sed',
            "'s/\ //g'")

        self.closed = True
        self.save_json()
        self.next_state()  # Done

    def next_state(self):
        self._state = next(self._state_iter)
        self._progress = None

    def factory_wipe(self):
        """
        Remove all the data and return to the factory image.

        :return: Returns the error code.
        :rtype: int
        """
        self.wait_for(State.RECOVERY)
        proc = cmd.run(self.adb, 'shell', 'recovery', '--wipe_data')
        return proc.returncode

    def reboot(self, state=None):
        """
        Reboot device, if no state is give, default state will be set.

        :param state: State
        :return: None
        """
        state = state or State.DEFAULT
        self.logger.debug('Rebooting into \'{}\'.'.format(state.value))
        cmd.run(*self.adb, 'reboot', state.value)

    def unmount(self, block):
        """
        Unmount a device or partition.

        :param block:
        :return:
        """
        # noinspection SpellCheckingInspection
        cmd.run(*self.shell, 'umount', block)

    def set_state(self, mode: State):
        """
        Reboot into recovery mode and waits for 5 seconds if device is
        already in recovery mode.

        :return:
        """
        adb = 'timeout', '10', *self.adb

        with suppress(subprocess.CalledProcessError):
            state = cmd.run(*adb, 'get-state').stdout
            if mode.value in state:
                return

            cmd.run(*adb, 'reboot', mode.value)

    def uptime(self):
        """
        Returns the uptime of the device.

        :return:
        """
        return parse_strings.uptime(
            cmd.run(*self.shell, 'cat', '/proc/uptime').stdout)

    def erase_data_partition(self, steps=1):
        block = None

        while not block:
            partitions = self.get_partitions()
            if '/data' in partitions:
                block = partitions['/data']
                self.logger.debug(
                    'Data partition found, mount point at \'{}\''.format(
                        block))

            else:
                uptime, _ = self.uptime()
                if uptime < 10:
                    self.logger.debug('Too early to find data partition.')
                    time.sleep(1)
                    continue

                raise Exception('No user partition found.')

        erasure = {
            'type': 'EraseBasic',
            'error': False,
            'zeros': True,
            # 'startTime': datetime.datetime.now(datetime.timezone.utc),
            'startTime': time.time(),
            'endTime': None,
            'steps': []
        }

        # Unmount block.
        self.unmount(block)
        # Todo: Check that dd fulfilled the entire partition.

        for _ in range(steps):
            # Erase data.
            self.logger.debug('Erasing block \'{}\'.'.format(block))
            step_event = {
                'type': 'StepZeros',
                'startTime': time.time(),
                'endTime': None,
                'error': False
            }

            proc = cmd.run(*self.shell, 'dd',
                           'if=/dev/zero',
                           'of={}'.format(block),
                           check=False)

            step_event['endTime'] = time.time()
            if proc.returncode != 0:
                step_event['error'] = True

            erasure['steps'].append(step_event)

        # Re-format.
        self.format_data()

        # erasure['endTime'] = datetime.datetime.now(datetime.timezone.utc)
        erasure['endTime'] = time.time()
        self.events.append(erasure)

    def format_data(self):
        """
        Send twrp command to format data partition.

        :return:
        """
        self.logger.debug('Reformat partitions.')
        proc = cmd.run(*self.shell, 'twrp', 'wipe', 'data', check=False)

        if proc.returncode != 0:
            raise ErasureFailedException(
                'Failed to reformat default data partitions')

    def install_os(self):
        self.wait_for(State.FLASH)

        # erasure = {
        #     'type': 'EraseBasic',
        #     'error': False,
        #     'zeros': False,
        #     'startTime': datetime.datetime.now(datetime.timezone.utc),
        #     'steps': []
        # }
        # # Todo: Install new OS.
        # self.unmount(block)
        # self.events.append(erasure)

    def save_json(self):
        with self.json_path.open('w') as f:
            # noinspection SpellCheckingInspection
            json.dump({
                'device': {
                    'type': 'Smartphone',  # Todo: Implementation for tablets.
                    'model': self.model,
                    'manufacturer': self.manufacturer,
                    'serialNumber': self.serial_number,
                    'imei': self.imei,
                },
                'closed': self.closed,
                'events': self.events
            }, f, cls=ereuse_utils.JSONEncoder, indent=2, sort_keys=True)

    def get_model(self):
        """
        Get the current model name of the device.

        :return: Model name.
        :rtype: str
        """
        try:
            return parse_strings.simple_string(
                cmd.run(*self.getprop, 'ro.product.model').stdout)

        except subprocess.CalledProcessError:
            raise DeviceNotConnectedException(
                'Device \'{}\' not connected.'.format(self.serial_number))

    def get_manufacturer(self):
        try:
            return parse_strings.simple_string(
                cmd.run(*self.getprop, 'ro.product.manufacturer').stdout)

        except subprocess.CalledProcessError:
            raise DeviceNotConnectedException(
                'Device \'{}\' not connected.'.format(self.serial_number))

    def get_partitions(self) -> dict:
        return parse_strings.get_partitions(
            cmd.run(*self.shell, 'mount').stdout)

    def flash_recovery(self):
        """
        Flash the recovery partition with the image from resources.

        Raises:
            ImageNotFoundException: When the image of the recovery isn't
                found.

        :return:
        """
        recovery_file = self._resources / 'recovery.img'
        flash_path = recovery_file.absolute().as_posix()

        if not recovery_file.exists():
            raise ImageNotFoundException(
                'The path {} is empty.'.format(flash_path))

        self.wait_for(State.FLASH)
        try:
            proc = cmd.run(*self.flash, 'flash', '--RECOVERY', flash_path)

        except subprocess.CalledProcessError:
            raise DeviceNotConnectedException(
                'Device \'{}\' not connected.'.format(self.serial_number))

        print(proc.stdout)

    def __hash__(self) -> int:
        return self.serial_number.__hash__()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, str):
            return o == self.serial_number
        return super().__eq__(o)

    def __repr__(self) -> str:
        return '<Mobile {0.serial_number}: {0._state.name}>'.format(self)

    def __str__(self) -> str:
        return '{0.model} {0.serial_number}: {0._state.value}'.format(self)


class Fastboot(threading.Thread):
    """Gets the state of a device in fastboot,
    flashing it if not done already.
    """

    def __init__(self, res: pathlib.Path):
        super().__init__(daemon=True)
        self.res = res

    def run(self) -> None:
        while True:
            with suppress(subprocess.CalledProcessError):
                subprocess.run(
                    ('heimdall', 'flash', '--RECOVERY',
                     str(self.res / 'recovery.img')),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            time.sleep(2)


class NoDevice(Exception):
    """There is not a new device."""
