import collections
import pathlib
from contextlib import suppress
from time import sleep

from workbench_android.mobile import Mobile, NoDevice


class WorkbenchAndroid:
    def __init__(self, save: pathlib.Path) -> None:
        super().__init__()
        self.mobiles = collections.deque()

    def loop_checking_new(self):
        """Stays in a forever loop initiating new plugged-in mobiles."""
        while True:
            with suppress(NoDevice):
                self.mobiles.append(Mobile.from_recovery(line))
            sleep(1)
