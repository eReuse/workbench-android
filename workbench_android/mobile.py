import subprocess
import threading
from enum import Enum
from time import sleep
from typing import Tuple, Union

from workbench_android.progressive_cmd import ProgressiveCmd


class Mobile(threading.Thread):
    class States(Enum):
        Bootloader = 'In Bootloader'
        InstallingRecovery = 'Installing the recovery'
        WaitingForRecovery = 'Waiting for the recovery'
        Erasing = 'Erasing'
        InstallingOS = 'Installing the OS'
        InstallingGapps = 'Installing the Google Apps'
        BootingIntoOS = 'Done. Check that the OS boots well.'

    def __init__(self, serial_number: str):
        super().__init__(daemon=True)
        self.serial_number = serial_number
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

        self.next_state()  # Installing recovery
        self._progress = ProgressiveCmd('execute',
                                        'heimdall/fastboot',
                                        'install custom recovery')
        self._progress.run()

        self.next_state()  # Waiting for booting into recovery
        self.wait_for_recovery()

        self.next_state()  # Erasing
        self._progress = ProgressiveCmd('adb', 'shell', 'dd')
        self._progress.run()

        self.next_state()  # Installing OS
        self._progress = ProgressiveCmd('adb', 'sideload', 'os')
        self._progress.run()

        self.next_state()  # Installing gapps
        self._progress = ProgressiveCmd('adb', 'sideload', 'gapps')
        self._progress.run()

        self.next_state()  # Booting into OS
        subprocess.run(('adb', 'reboot'), universal_newlines=True, check=True)

    def next_state(self):
        self._state = next(self._state_iter)
        self._progress = None

    def wait_for_recovery(self):
        while True:
            result = subprocess.run(('adb', 'devices', '--serial', self.serial_number),
                                    universal_newlines=True,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    check=True)
            if self.device_found(result.stdout):
                break
            sleep(1)

    @classmethod
    def factory_from_bootloader(cls):
        """Starts processing new mobiles found in heimdall/fastboot."""
        result = subprocess.run(('heimdall/fastboot', 'detect/devices'),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,
                                check=True)
        try:
            sn = cls.get_serial_number(result.stdout)
        except ValueError:
            raise NoDevice()
        else:
            mobile = cls(sn)
            mobile.start()
            return mobile

    def device_found(self, out: str):
        raise NotImplementedError()  # todo

    @classmethod
    def get_serial_number(cls, out: str):
        raise NotImplementedError()  # todo

    def __repr__(self) -> str:
        return '<Mobile {0.serial_number}: {0._state.name}>'.format(self)

    def __str__(self) -> str:
        return '{0.serial_number}: {0._state.value}'.format(self)


class NoDevice(Exception):
    """There is not a new device."""
