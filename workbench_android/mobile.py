import datetime
import json
import math
import pathlib
import subprocess
import threading
from contextlib import suppress
from enum import Enum
from time import sleep
from typing import Dict, Set, Tuple, Union

import ereuse_utils
import yaml
from ereuse_utils import cli, cmd, text
from ereuse_utils.naming import Naming


class Adb:
    def __init__(self, serial_number: str) -> None:
        self.serial_number = serial_number
        self.adb = 'adb', '-s', self.serial_number
        self.sh = self.adb + 'shell',
        self.dumpsys = self.shell('dumpsys')

    def prop(self, prop: str) -> str:
        return cmd.run(*self.sh, 'getprop', prop).stdout.strip()

    def shell(self, *params) -> str:
        return cmd.run(*self.sh, *params).stdout.strip()


class Mobile(threading.Thread):
    @classmethod
    def new(cls, mobiles, save_dir: pathlib.Path, line: cli.Line):
        result = cmd.run('adb', 'devices')
        for line in result.stdout.splitlines()[1:]:
            try:
                sn, _ = line.split()
            except ValueError:
                pass
            else:
                if sn and sn not in mobiles:
                    # The SN is new and the device is in recovery
                    mobile = cls(sn, save_dir, line)
                    cls._mobiles.add(mobile)
                    mobile.start()
                    return mobile
        raise NoDevice()

    def __init__(self, serial_number: str, res: pathlib.Path, jsons: pathlib.Path):
        self.serial_number = serial_number
        self.adb = Adb(serial_number)
        self.props = self._get_properties()
        self.model = self.props['ro.product.model']
        self.manufacturer = self.props['ro.product.manufacturer']
        self.imei = None
        self.closed = False
        self.dir = res / self.model
        self.events = []
        super().__init__(daemon=True)
        hid = Naming.hid('Smartphone', self.manufacturer, self.model, self.serial_number)
        self.json_path = jsons / (hid + '.json')
        self.save_json()
        self._state_iter = iter(self.States)
        self._state = next(self._state_iter)
        self._progress = None  # type: Union[ProgressiveCmd, None]
        self._error = None
        self.components = []

    def _get_properties(self) -> Dict[str, object]:
        properties = self.adb.shell('getprop').replace('[', '').replace(']', '')
        return yaml.load(properties)

    @classmethod
    def from_recovery(cls, snapshot: pathlib.Path, line: cli.Line):
        """Starts processing a new mobile that is in recovery."""


class Display():
    def __init__(self, adb: Adb) -> None:
        display_info = text.grep(adb.dumpsys, 'PhysicalDisplayInfo')
        self.resolution_width, self.resolution_height, self.refresh_rate, _internal_density, \
        self.density_width, self.density_height, *_ = text.numbers(display_info)

        self.size = math.sqrt(
            (self.resolution_width / self.density_width) ** _internal_density +
            (self.resolution_height / self.density_height) ** _internal_density
        )
        """Size. From https://stackoverflow.com/a/19446138/2710757."""
        self.technology = None
        self.contrast_ratio = None
        self.touchable = True


class Processor:
    def __init__(self, adb: Adb) -> None:
        self.cores = len(tuple(text.numbers(adb.shell('ls', '/sys/devices/system/cpu'))))


class RamModule:
    def __init__(self, adb: Adb) -> None:
        super().__init__()
        meminfo = adb.shell('cat', '/proc/meminfo')
        # Ram is in KB
        self.total = next(text.numbers(text.grep(meminfo, 'MemTotal'))) // 1000


class GraphicCard:
    def __init__(self, adb: Adb) -> None:
        super().__init__()
        gpu = text.grep(adb.dumpsys, 'GLES:')
        self.manufacturer, self.model, *_ = gpu.split(', ')


class DataStorage:
    def __init__(self, adb: Adb) -> None:
        self.size = next(text.numbers(text.grep(adb.dumpsys, 'System Size:'))) // (1 * 10) ^ 6


class NetworkAdaptor:

    def __init__(self, adb: Adb) -> None:
        self.macs = {
            next(text.macs(text.grep(adb.shell('ip', 'addr', 'show'), 'link/ether')))
        }
        self.bluetooth_mac = adb.shell('settings get secure bluetooth_address')


class Battery:
    def __init__(self, adb: Adb) -> None:
        props = adb.shell('dumpsys', 'battery')
        props = yaml.load(props)['Current Battery Service state']
        self.wireless = props['Wireless powered']
        self.status = props['status']
        self.health = props['health']
        self.voltage = props['voltage']
        self.technology = props['technology']
        self.charge_counter = props['Charge counter']
        self.size = next(
            text.numbers(text.grep(adb.dumpsys, 'Estimated battery capacity:')))  # mAh


class Camera:

    def __init__(self, *args) -> None:
        pass

    def new(self, adb: Adb):
        for model in text.grep(adb.dumpsys, 'camera-name'):
            video = next(text.grep(adb.dumpsys, 'video-size-values'),
                         text.grep(adb.dumpsys, 'preview-size-values'))
            v_height, v_width, *_ = text.numbers(video)
            cam = Camera(model=model,
                         height=next(text.grep(adb.dumpsys, 'raw-height')),
                         width=next(text.grep(adb.dumpsys, 'raw-width')),
                         focal_length=next(text.grep(adb.dumpsys, 'focal-length')),
                         video_height=v_height,
                         video_width=v_width
                         )


class Mobile(threading.Thread):
    _mobiles = set()  # type: Set[Mobile]

    class States(Enum):
        Recovery = 'In recovery'
        Erasing = 'Erasing'
        WaitingSideload = 'Go to sideload'
        InstallingOS = 'Installing the OS'
        WaitSideloadAgain = 'Installed. Relaunch sideload to install Google Apps.'
        InstallingGapps = 'Installing the Google Apps'
        BootingIntoOS = 'Booting into OS... don\'t disconnect.'
        Done = 'Done. Check everything works well.'

    class Modes(Enum):
        Recovery = 'recovery'
        Sideload = 'sideload'
        Device = 'device'

        def in_recovery(self):
            """Recovery englobes some states, like sideload."""
            return self in {self.Recovery, self.Sideload}

    def __init__(self, serial_number: str, res: pathlib.Path, jsons: pathlib.Path):
        self.serial_number = serial_number
        self.adb = 'adb', '-s', self.serial_number
        getprop = self.adb + ('shell', 'getprop')
        self.model = cmd.run(*getprop, 'ro.product.model').stdout.strip()
        self.manufacturer = cmd.run(*getprop, 'ro.product.manufacturer').stdout.strip()
        self.imei = None
        self.closed = False
        self.dir = res / self.model
        self.events = []
        super().__init__(daemon=True)
        hid = Naming.hid('Smartphone', self.manufacturer, self.model, self.serial_number)
        self.json_path = jsons / (hid + '.json')
        self.save_json()
        self._state_iter = iter(self.States)
        self._state = next(self._state_iter)
        self._progress = None  # type: Union[ProgressiveCmd, None]
        self._error = None

    def status(self) -> Tuple[States, Union[int, None], Union[str, None]]:
        """Returns information of the process of this mobile.

        Returns the state and, if the state is a progress,
        the number steps performed from the last time this method
        was executed.
        """
        return self._state, self._progress.increment() if self._progress else None, self._error

    def run(self):
        try:
            self._run()
        except subprocess.CalledProcessError as e:
            self._error = '{}: {}'.format(e, e.stderr)

    def _run(self):
        """Processes the device, erasing it, installing the OS, etc."""
        # todo check if adb devices -- recovery or device?

        # Initial state is Recovery

        self.next_state()  # Erasing
        self.erase_data_partition()

        self.next_state()  # Waiting for sideload
        self.wait_until_mode(self.Modes.Sideload)

        self.next_state()  # Installing OS
        start = datetime.datetime.now(datetime.timezone.utc)
        os = 'samsung.zip'
        self._progress = ProgressiveCmd(*self.adb, 'sideload', self.dir / os,
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
        self.wait_until_mode(self.Modes.Recovery)
        self.wait_until_mode(self.Modes.Sideload)

        self.next_state()  # Installing gapps
        self._progress = ProgressiveCmd(*self.adb, 'sideload', self.dir / 'gapps.zip',
                                        stdout=subprocess.PIPE,
                                        number_chars=2,
                                        read=10)
        self._progress.run()

        self.wait_until_mode(self.Modes.Recovery)
        self.next_state()  # Booting into OS
        cmd.run(*self.adb, 'reboot')
        self.wait_until_mode(self.Modes.Recovery)
        self.save_json()
        self.wait_until_mode(self.Modes.Device)
        # get imei from https://android.stackexchange.com/a/194514
        # only works when main OS is already booting
        self.imei = cmd.run(*self.adb, 'shell', 'service', 'call', 'iphonesubinfo', 1, '|',
                            'toybox', 'cut', '-d', "'", '-f2', '|', 'toybox', 'grep', '-Eo',
                            "'[0-9]'", '|', 'toybox', 'xargs', '|', 'toybox', 'sed', "'s/\ //g'")
        self.closed = True
        self.save_json()
        self.next_state()  # Done

    def next_state(self):
        self._state = next(self._state_iter)
        self._progress = None

    @classmethod
    def factory_from_recovery(cls, res: pathlib.Path, jsons: pathlib.Path):
        """Starts processing a new mobile that is in recovery."""
        result = cmd.run('adb', 'devices')
        for line in result.stdout.splitlines()[1:]:
            try:
                sn, mode = line.split()
                mode = cls.Modes(mode)
            except ValueError:
                pass
            else:
                if sn and sn not in cls._mobiles and mode.in_recovery():
                    # The SN is new and the device is in recovery
                    mobile = cls(sn, res, jsons)
                    cls._mobiles.add(mobile)
                    mobile.start()
                    return mobile
        raise NoDevice()

    def device_found(self, out: str):
        raise NotImplementedError()  # todo

    @classmethod
    def get_serial_number(cls, out: str):
        raise NotImplementedError()  # todo

    def wait_until_mode(self, mode: Modes):
        """Blocks until it gets the actual mode of the device"""
        while True:
            with suppress(ValueError, StopIteration):
                r = cmd.run('adb', 'devices')
                m = next(l.split()[1] for l in r.stdout.splitlines() if self.serial_number in l)
                if mode == self.Modes(m):
                    return
            sleep(1)

    def erase_data_partition(self):
        shell = 'adb', '-s', self.serial_number, 'shell'
        i = 1
        while True:
            try:
                sleep(1)
                cmd.run(*shell, 'recovery', '--set_filesystem_encryption=off')
                cmd.run(*shell, 'twrp', 'wipe', 'data')
                sleep(1)
                res = cmd.run(*shell, 'mount')
                part = next(line.split()[0] for line in res.stdout.splitlines() if '/data' in line)
            except (StopIteration, subprocess.CalledProcessError) as e:
                i += 1
                self._error = 'Data partition broken. Wiping again... ({}) ({})'.format(i, e)
                sleep(5)
            else:
                self._error = None
                break
        erasure = {
            'type': 'EraseBasic',
            'error': False,
            'zeros': False,
            'startTime': datetime.datetime.now(datetime.timezone.utc),
            'steps': []
        }
        # todo check that dd fulfilled the entire partition
        cmd.run(*shell, 'dd', 'if=/dev/zero', 'of={}'.format(part), check=False)
        cmd.run(*shell, 'twrp', 'wipe', 'data')
        erasure['endTime'] = datetime.datetime.now(datetime.timezone.utc)
        erasure['steps'].append({
            'type': 'StepRandom',
            'startTime': erasure['startTime'],
            'endTime': erasure['endTime'],
            'error': False
        })
        self.events.append(erasure)

    def save_json(self):
        with self.json_path.open('w') as f:
            json.dump({
                'device': {
                    'type': 'Smartphone',  # todo check for tablets!
                    'model': self.model,
                    'manufacturer': self.manufacturer,
                    'serialNumber': self.serial_number,
                    'imei': self.imei,
                },
                'closed': self.closed,
                'events': self.events
            }, f, cls=ereuse_utils.JSONEncoder, indent=2, sort_keys=True)

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
                    ('heimdall', 'flash', '--RECOVERY', str(self.res / 'recovery.img')),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            sleep(2)


class NoDevice(Exception):
    """There is not a new device."""
