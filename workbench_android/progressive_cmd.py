import subprocess
from contextlib import suppress
from typing import Any, TextIO


class ProgressiveCmd:
    """Executes a cmd while interpreting its completion percentage.

    The completion percentage of the cmd is stored in
    :attr:`.percentage` and the user can obtain percentage
    increments by executing :meth:`.increment`.

    This class is useful to use within a child thread, so a main
    thread can request from time to time the percentage / increment
    status of the running command.
    """
    READ_LINE = None
    DECIMALS = 5
    INT = 3

    def __init__(self, *cmd: Any,
                 stdout=subprocess.DEVNULL,
                 number_chars: int = INT,
                 read: int = READ_LINE):
        """
        :param cmd: The command to execute.
        :param stderr: the stderr passed-in to Popen.
        :param stdout: the stdout passed-in to Popen
        :param number_chars: The number of chars used to represent
                             the percentage. Normalized cases are
                             :attr:`.DECIMALS` and :attr:`.INT`.
        :param read: For commands that do not print lines, how many
                     characters we should read between updates.
                     The percentage should be between those
                     characters.
        """
        self.cmd = tuple(str(c) for c in cmd)
        self.read = read
        self.step = 0
        self.number_chars = number_chars
        # We call subprocess in the main thread so the main thread
        # can react on ``CalledProcessError`` exceptions
        self.conn = conn = subprocess.Popen(self.cmd,
                                            universal_newlines=True,
                                            stderr=subprocess.PIPE,
                                            stdout=stdout)
        self.out = conn.stdout if stdout == subprocess.PIPE else conn.stderr  # type: TextIO
        self.last_update_percentage = 0
        self.percentage = 0

    def run(self) -> None:
        """Processes the output."""
        while True:
            out = self.out.read(self.read) if self.read else self.out.readline()
            if out:
                with suppress(ValueError):
                    i = out.rindex('%')
                    try:
                        self.percentage = int(float(out[i - self.number_chars:i]))
                    except ValueError:  # case when value is only one char (0 - 9)
                        self.percentage = int(float(out[i - (self.number_chars - 1):i]))
            else:  # No more output
                break
        if self.conn.wait() == 1:  # wait until cmd ends
            raise subprocess.CalledProcessError(self.conn.returncode,
                                                self.conn.args,
                                                stderr=self.conn.stderr.read())
        self.percentage = 100  # some cmds do not output 100 when completed

    def increment(self):
        """Returns the increment of progression from
        the last time this method is executed.
        """
        # for cmd badblocks the increment can be negative at the
        # beginning of the second step where last_percentage
        # is 100 and percentage is 0. By using max we
        # kind-of reset the increment and start counting for
        # the second step
        increment = max(self.percentage - self.last_update_percentage, 0)
        self.last_update_percentage = self.percentage
        return increment
