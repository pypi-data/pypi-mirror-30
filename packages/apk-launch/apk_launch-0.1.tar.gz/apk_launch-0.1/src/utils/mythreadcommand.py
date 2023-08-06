"""
mythreadcommand is a helper library for running bash commands in python thread.

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
import threading


class ThreadedCommand(threading.Thread):
    """This class helps you to run a command from a thread and get output."""

    def __init__(self, cmd, cwd=None, printout=False, error_pattern=None):
        """
        Initialize ThreadedCommand object with args.

        Args:
            cmd: command list to run
            cwd: directory to execute from
            printout: print output to stdout
            error_pattern: pattern(s) to search for

        Returns:
            None

        """
        self.cmd = cmd
        self.cwd = cwd
        self.printout = printout
        self.process = None
        self.log = []
        self.returncode = -1
        self.error_pattern = None
        if error_pattern:
            if isinstance(error_pattern, list):
                self.error_pattern = error_pattern
            else:
                self.error_pattern = [error_pattern]

        threading.Thread.__init__(self)

    def run(self):
        """
        Run ThreadedCommand.

        Args:
            None

        Returns:
            list of output if no error and wait=True, else None

        """
        if self.cwd:
            self.process = subprocess.Popen(self.cmd.split(),
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, bufsize=1,
                                            shell=False,
                                            universal_newlines=True,
                                            cwd=self.cwd)
        else:
            self.process = subprocess.Popen(self.cmd.split(),
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, bufsize=1,
                                            shell=False,
                                            universal_newlines=True)
        output, _ = self.process.communicate()
        self.log = output

    def get_log(self):
        """
        Return log from command.

        Args:
            None

        Returns:
            list of output

        """
        return self.log
