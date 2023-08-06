"""
mycommand is a helper library for running bash commands in python.

    Copyright (C) 2018 Zach Yannes
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
import subprocess
import re
import signal
import logging

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(format='%(message)s', level=logging.INFO)
LOG = logging.getLogger(__name__)


class Alarm(Exception):
    """Used to set timer for command."""

    pass


def alarm_handler(signum, frame):
    """
    Raise Alarm Exception after timer.

    Args:
        signum: signal number
        frame: frame where alarm is handled

    Returns:
        None

    Raises:
        Alarm

    """
    # pylint: disable=unused-argument
    raise Alarm


class Command(object):
    """This class helps you to run a command and get output."""

    def __init__(self, cmd, cwd=None, queue=None, printout=False):
        """
        Initialize Command object with args.

        Args:
            cmd: command list to run
            cwd: directory to execute from
            printout: print output to stdout

        Returns:
            None

        """
        self.cmd = cmd
        self.cwd = cwd
        self.process = None
        self.printout = printout
        self.log = []
        self.queue = queue

    def run(self, wait=True, error_pattern=None, timeout=0):
        """
        Initialize Command object with args.

        Args:
            wait: wait for command to finish
            error_pattern: error pattern to search for
            timeout: if > 0, set timeout alarm

        Returns:
            list of output if no error and wait=True, else None

        """
        if error_pattern and not isinstance(error_pattern, list):
            error_pattern = [error_pattern]
        LOG.debug('Running command: %s', self.cmd)
        if self.cwd:
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, bufsize=1,
                                            shell=True, universal_newlines=True,
                                            cwd=self.cwd)
        else:
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, bufsize=1,
                                            shell=True, universal_newlines=True)

        if wait:
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(timeout)
            try:
                for line in iter(self.process.stdout.readline, ''):
                    line = line.strip()
                    if self.printout:
                        LOG.info(line)
                    self.log.append(line)
                    if self.check_for_errors(error_pattern, line):
                        signal.alarm(0)
                        return None
                self.process.stdout.close()
                self.process.wait()
                signal.alarm(0)
            except Alarm:
                LOG.error('%s timed out after %s seconds',
                          self.cmd, timeout)

        signal.alarm(0)
        return self.log

    def wait(self):
        """
        Wait for command to complete.

        Args:
            None

        Returns:
            list of output, else None

        """
        # self.process.wait()
        outs, _ = self.process.communicate()
        # LOG.debug('{}: output {}, stderr {}'.format(self.cmd, outs, errs))
        self.log = outs.rstrip()
        return self.log

    def check_for_errors(self, patterns, line):
        """
        Check line for error.

        Args:
            line: line to check

        Returns:
            True if error, else False

        """
        if not patterns:
            return False
        for pattern in patterns:
            if self.check_error(pattern, line):
                LOG.error('Error running "%s" in %s', self.cmd, self.cwd)
                self.process.kill()
                return True
        return False

    @staticmethod
    def check_error(pattern, line):
        """
        Check line for error pattern.

        Args:
            pattern: error pattern
            line: line to check

        Returns:
            True if error, else False

        """
        match = re.match(pattern, line)
        if not match:
            return False
        data = match.groupdict()
        if not data:
            return False
        return True

    def get_log(self):
        """
        Return log from command.

        Args:
            None

        Returns:
            list of output

        """
        return self.log
