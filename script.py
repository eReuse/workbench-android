import sys
import time
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

# Erase step.
# m.set_state(mobile.State.RECOVERY)
# result = m.erase_data_partition()

print(m.state())

