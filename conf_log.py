import logging
from workbench_android import workbench_android
LOGGING_LEVEL = logging.DEBUG
FORMATTER_PRETTY = '[%(asctime)s][%(levelname)s]: %(message)s'


def configure(level=LOGGING_LEVEL):
    """
    Configure the the logging system.

    Args:
        level (int): Logging level.
    """
    logging.basicConfig(format=FORMATTER_PRETTY, datefmt='%H:%M:%S,%3d', )

    script_logger = logging.getLogger("Workbench-android")
    script_logger.setLevel(level)

    wba_logger = logging.getLogger(workbench_android.WorkbenchAndroid.__name__)
    wba_logger.setLevel(level)
