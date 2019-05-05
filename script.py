import sys
import logging

from pathlib import Path

from workbench_android import mobile

# noinspection SpellCheckingInspection
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)

res = Path('resources')
out = Path('outputs')
m = mobile.Mobile('21f4c3ce', res, out, [handler])

# Todo: Root recovery.

# Erase data partitions.
m.erase_data_partition()

# Reformat partitions and reboot.
m.format_data()
m.reboot(mobile.State.RECOVERY)

# Todo: Install new OS.

# Todo: Install apps.

m.save_json()
