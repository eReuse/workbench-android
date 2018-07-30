import collections
from contextlib import suppress

import blessed
import click
import colorama

from workbench_android.mobile import Mobile, NoDevice


def manual_spinner():
    while True:
        for cursor in '|/-\\':
            yield cursor


SPACE = 70
"""Where to print bar / spinners."""

UPDATE_SPEED = 0.3
"""Seconds that the main thread takes to cycle between updates."""


@click.command()
def main():
    """
    Obtains info of Android devices, jailbreaks them,
    erases them, and installs a custom free community-picked
    Android distribution.
    """
    term = blessed.Terminal()
    mobiles = collections.deque()
    spinner = manual_spinner()
    with term.fullscreen(), term.cbreak():
        title = 'eReuse.org Workbench Android. Detecting Androids'
        print(title)
        print('{}Press \'q\' to quit.{}'.format(colorama.Style.DIM, colorama.Style.RESET_ALL))
        while term.inkey(timeout=UPDATE_SPEED).lower() != 'q':
            spin_step = next(spinner)
            with term.location(len(title) + 1, 0):
                print(spin_step)

            # Is there a new mobile?
            with suppress(NoDevice):
                mobiles.append({
                    'mobile': Mobile.factory_from_bootloader(),
                    'last_state': None,
                    'bar': None
                })
            # Update mobiles
            for i, info in enumerate(mobiles, start=3):
                state, increment = info['mobile'].status()
                if info['last_state'] == state:
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
