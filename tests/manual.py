from random import random
from time import sleep
from unittest import mock
from unittest.mock import MagicMock

from workbench_android.main import Mobile, main

"""Manual testing of workbench android.

Execute it like this: ``python3 tests/manual.py``.
"""


def _run(*cmd, **kwargs):
    sleep(0.25)
    return MagicMock()


@classmethod
def _sn(cls, _):
    if not hasattr(cls, '_x'):
        cls._x = 0
    if cls._x > 5:
        raise ValueError()
    if random() > 0.2:
        raise ValueError()  # No new devices
    cls._x += 1
    return 'Galaxy Nexus A38487X-{}'.format(cls._x)


def lines():
    l = ['10%', '20%', '30%', '40%', '50%', '80%', '100%']
    while True:
        for li in l:
            li = li.rjust(10)
            sleep(3)
            yield li
        yield None


class Popen:
    def __init__(self) -> None:
        self.percentages = '10%', '20%', '30%', '40%', '50%', '80%', '100%'
        self.iter = iter(self.percentages)
        self.stderr = self

    def readline(self):
        try:
            sleep(random() * 5)
            return next(self.iter).rjust(5)
        except StopIteration:
            return None


Mobile.get_serial_number = _sn
Mobile.device_found = lambda *args, **kwargs: bool(not sleep(3))
with mock.patch('subprocess.run') as run, mock.patch('subprocess.Popen') as popen:
    run.side_effect = _run
    popen.side_effect = lambda *args, **kwargs: Popen()

    main()
