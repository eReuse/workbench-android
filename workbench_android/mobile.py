import pathlib
import subprocess
import threading
from enum import Enum
from time import sleep
from typing import Deque, Tuple, Union

from workbench_android.progressive_cmd import ProgressiveCmd


class Mobile(threading.Thread):
    class States(Enum):
        Recovery = 'In recovery'
        Erasing = 'Erasing'
        InstallingOS = 'Installing the OS'
        InstallingGapps = 'Installing the Google Apps'
        BootingIntoOS = 'Done. Check that the OS boots well.'

    def __init__(self, serial_number: str, res: pathlib.Path):
        super().__init__(daemon=True)
        self.serial_number = serial_number
        self.res = res
        self._state_iter = iter(self.States)
        self._state = next(self._state_iter)
        self._progress = None  # type: Union[ProgressiveCmd, None]

    def status(self) -> Tuple[States, Union[int, None]]:
        """Returns information of the process of this mobile.

        Returns the state and, if the state is a progress,
        the number steps performed from the last time this method
        was executed.
        """
        return self._state, self._progress.increment() if self._progress else None

    def run(self):
        """Processes the device, erasing it, installing the OS, etc."""
        # todo check if adb devices -- recovery or device?

        self.next_state()  # Erasing
        self.erase_data_partition()

        self.next_state()  # Installing OS
        self._progress = ProgressiveCmd('adb', '-s', self.serial_number, 'sideload', self.res / 'os.zip')
        self._progress.run()

        self.next_state()  # Installing gapps
        self._progress = ProgressiveCmd('adb', '-s', self.serial_number, 'sideload', self.res / 'gapps.zip')
        self._progress.run()

        self.next_state()  # Booting into OS
        subprocess.run(('adb', 'reboot'), universal_newlines=True, check=True)

    def next_state(self):
        self._state = next(self._state_iter)
        self._progress = None

    @classmethod
    def factory_from_recovery(cls, res: pathlib.Path, mobiles: Deque['Mobile']):
        """Starts processing new mobiles found in heimdall/fastboot."""
        result = subprocess.run(('adb', 'devices'),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,
                                check=True)
        # todo process all lines
        sn, mode = result.stdout.splitlines()[1].split()
        if sn and mode == 'recovery':
            if sn not in mobiles:
                mobile = cls(sn, res)
                mobile.start()
                return mobile
        else:
            raise NoDevice()

    def device_found(self, out: str):
        raise NotImplementedError()  # todo

    @classmethod
    def get_serial_number(cls, out: str):
        raise NotImplementedError()  # todo

    def erase_data_partition(self):
        shell = 'adb', '-s', self.serial_number, 'shell'
        result = subprocess.run(shell + ('mount',),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,
                                check=True)
        partition = next(line.split()[0] for line in result.stdout if '/data' in line)
        subprocess.run(shell + ('dd', 'if=/dev/zero', 'of={}'.format(partition)), check=True)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, str):
            return o == self.serial_number
        return super().__eq__(o)

    def __repr__(self) -> str:
        return '<Mobile {0.serial_number}: {0._state.name}>'.format(self)

    def __str__(self) -> str:
        return '{0.serial_number}: {0._state.value}'.format(self)


class Fastboot(threading.Thread):
    """Gets the state of a device in fastboot,
    flashing it if not done already.
    """

    class States(Enum):
        Empty = 'No devices found in bootloader.'
        InstallingRecovery = 'Installing the recovery'

    def __init__(self, res: pathlib.Path):
        super().__init__(daemon=True)
        self.state = self.States.Empty
        self.res = res

    def run(self) -> None:
        while True:
            self.state = self.States.Empty
            try:
                subprocess.run(('heimdall', 'detect'), check=True)
            except subprocess.CalledProcessError:
                sleep(1)
            else:
                self.state = self.States.InstallingRecovery
                subprocess.run(
                    ('heimdall', 'flash', '--RECOVERY', str(self.res / 'recovery.img')),
                    check=True
                )


class NoDevice(Exception):
    """There is not a new device."""
