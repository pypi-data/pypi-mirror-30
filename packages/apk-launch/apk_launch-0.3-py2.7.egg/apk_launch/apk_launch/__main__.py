"""
__main__ launches apklaunch.

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
import os
import sys

import logging
import logging.handlers

from apk_launch.apk_launch import apklaunch

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger(__name__)

if 'JAVA_HOME' not in os.environ:
    print 'Error: Must have java installed'
    sys.exit(2)
elif not os.environ['JAVA_HOME']:
    if sys.platform == 'darwin':
        os.environ['JAVA_HOME'] = '/Library/Java/JavaVirtualMachines/jdk1.8.0_144.jdk/Contents/Home'
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        os.environ['JAVA_HOME'] = '/usr/lib/jvm/jdk1.8.0_121'
    LOG.debug('Updated JAVA_HOME to %s', os.environ['JAVA_HOME'])
else:
    LOG.debug('Using JAVA_HOME to %s', os.environ['JAVA_HOME'])

if __name__ == '__main__':
    RES = apklaunch.main()
    sys.exit(RES)
