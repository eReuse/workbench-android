import collections
import pathlib
import subprocess
from contextlib import suppress

import blessed
import click
import colorama

from workbench_android.mobile import Fastboot, Mobile, NoDevice

@click.command()







def manual_spinner():
    while True:
        for cursor in '|/-\\':
            yield cursor


SPACE = 70
"""Where to print bar / spinners."""

UPDATE_SPEED = 0.3
"""Seconds that the main thread takes to cycle between updates."""


# @click.command()
# @click.argument('res', type=cli.Path(exists=True, dir_okay=True))
def main(res: pathlib.Path, jsons: pathlib.Path):
    """Prepares Android smartphones for reuse.

    Obtains info of Android devices, jailbreaks them,
    erases them, and installs a custom free community-picked
    Android distribution.

    This software requires a path pointing to a RES folder.
    """
    term = blessed.Terminal()
    mobiles = collections.deque()
    spinner = manual_spinner()
    fastboot = Fastboot(res)
    fastboot.start()
    # Instantiate adb
    subprocess.run(('adb', 'start-server'))

    with term.fullscreen(), term.cbreak():
        title = 'eReuse.org Workbench Android. Detecting Androids'
        print(title)
        print('{}Press \'q\' to quit.{}'.format(colorama.Style.DIM, colorama.Style.RESET_ALL))
        while term.inkey(timeout=UPDATE_SPEED).lower() != 'q':
            spin_step = next(spinner)
            with term.location(len(title) + 1, 0):
                print(spin_step)

            # Is there a new mobile (in recovery?)
            with suppress(NoDevice):
                mobiles.append({
                    'mobile': Mobile.factory_from_recovery(res, jsons),
                    'last_state': None,
                    'bar': None
                })
            # Update mobiles
            for i, info in enumerate(mobiles, start=4):
                state, increment, error = info['mobile'].status()
                if error:
                    with term.location(0, i):
                        print('{}{}{}'.format(colorama.Fore.RED, error, colorama.Style.RESET_ALL))
                elif info['last_state'] == state:
                    if state != next(reversed(Mobile.States)):  # Last state
                        if increment:
                            with term.location(0, i):
                                info['bar'].update(increment)
                        elif increment is None:
                            with term.location(SPACE + 2, i):
                                print(spin_step)
                else:
                    with term.location(0, i):
                        print(term.clear_eol)  # Clear line
                    with term.location(0, i):
                        if increment is None:
                            print(info['mobile'])
                        else:
                            info['bar'] = click.progressbar(length=100,
                                                            label=str(info['mobile']).ljust(SPACE))
                            info['bar'].__enter__()
                info['last_state'] = state
    # subprocess.run(('adb', 'kill-server'))


main(pathlib.Path.home() / 'Documents' / 'wa', pathlib.Path.home() / 'Documents' / 'wa-jsons')
