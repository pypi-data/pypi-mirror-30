#!/usr/bin/env python
"""
gradle_parser is a helper library for parsing gradle gradle files.

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
import tempfile
import shutil
import re
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

BUILD_VERSION = '27.0.3'  # '26.0.1' # '25.0.3'
GRADLE_VERSION = '4.4.1'
GRADLE_CLASSPATH = '3.0.1'

VERSION_PATTERN = re.compile(r'buildToolsVersion (\'|")(?P<version>[\w\d\.]+)(\'|")')
DEFAULT_ERROR_PATTERN = re.compile(r'(?P<fail>FAILED)')
ANT_ERROR_PATTERN = re.compile(r'(?P<fail>BUILD FAILED)')
PATTERN_GRADLE_URL = re.compile(r'distributionUrl=(?P<url>.+)')
PATTERN_GRADLE_CLASSPATH = re.compile(r'classpath \'(?P<classpath>'
                                      r'com\.android\.tools\.build:gradle:.+)\'')


def get_depth(line):
    """
    Calculate depth of line by num of spaces.

    Args:
        line: line to check

    Returns:
        number of spaces in front of line

    """
    return len(line) - len(line.lstrip())


PATTERN_MAVEN = re.compile(r'(?P<maven>maven {)\s+(?P<urls>[^}]+)+}', re.MULTILINE)
PATTERN_REPOS = re.compile(r'(?P<repos>repositories {[^}]+})', re.MULTILINE)


def read_repositories(openfd, depth=0):
    """
    Read repositories in open file descriptor.

    Args:
        f: open file descriptor
        depth: current depth of line (num of spaces preceding) (defaults to 0)

    Returns:
        lines in file after altered

    """
    LOG.debug('Starting repositories: indent = %s', depth)
    # lines = ['{}repositories {{\n'.format(' ' * depth)]
    lines = []
    found_google = False
    found_jcenter = False
    while True:
        line = openfd.readline()

        LOG.debug('Repo line: "%s"', line)
        if not line:
            break
        if line.strip() == '}' and get_depth(line) == depth:
            if not found_google:
                lines.append('        google()\n')
            if not found_jcenter:
                lines.append('        jcenter()\n')
            # lines.append(line)
            break
        lines.append(line)
        if line.lstrip().startswith('google()'):
            found_google = True
        if line.lstrip().startswith('jcenter()'):
            found_jcenter = True
    LOG.debug('Repo: \n"%s"', lines)
    lines.append('    }\n')
    return lines


def fix_gradle(filename, dryrun=False):
    """
    Fix a build.gradle file.

    Args:
        filename: gradle file to fix
        dryrun: whether to write results to original file (defaults to False)

    Returns:
        None

    """
    all_lines = []
    with open(filename, 'r') as openfd:
        while True:
            line = openfd.readline()
            if not line:
                break

            all_lines.append(line)
            depth = get_depth(line)
            if 'repositories {' in line:
                lines = read_repositories(openfd, depth)
                LOG.debug('Read repositories:\n%s', ''.join(lines))
                all_lines += lines

    text = '\n'.join([line.rstrip() for line in all_lines])
    LOG.debug('All lines:\n%s', text)

    if dryrun:
        sys.exit(0)

    with open(filename, 'w') as openfd:
        openfd.write(''.join(all_lines))


def replace_gradle_classpath(file_path):
    """
    Replace classpath in gradle files.

    Args:
        file_path: path to file

    Returns:
        None

    """
    newline = (r'classpath \'com.android.tools.build:gradle:{}\''
               .format(GRADLE_CLASSPATH))
    LOG.debug('Replacing classpath in %s', file_path)
    tempfd, abs_path = tempfile.mkstemp()
    with open(abs_path, 'w') as new_file:
        if not os.path.isfile(file_path):
            return
        with open(file_path) as old_file:
            for line in old_file:
                result, count = re.subn(PATTERN_GRADLE_CLASSPATH, newline,
                                        line.rstrip())
                if count > 0:
                    LOG.debug('Replaced classpath with %s', result)
                new_file.write(result + '\n')
    os.close(tempfd)
    os.remove(file_path)
    shutil.move(abs_path, file_path)


def replace_gradle_url(file_path):
    """
    Replace gradle url in gradle file.

    Args:
        file_path: path to gradle file

    Returns:
        None

    """
    newline = (r'distributionUrl=http\://services.gradle.org/distributions/'
               'gradle-{}-bin.zip'.format(GRADLE_VERSION))
    LOG.debug('Replacing url in %s', file_path)
    tempfd, abs_path = tempfile.mkstemp()
    with open(abs_path, 'w') as new_file:
        if not os.path.isfile(file_path):
            return
        with open(file_path) as old_file:
            for line in old_file:
                result, count = re.subn(PATTERN_GRADLE_URL, newline, line.rstrip())
                if count > 0:
                    LOG.debug('Replaced url with %s', result)
                new_file.write(result + '\n')
    os.close(tempfd)
    os.remove(file_path)
    shutil.move(abs_path, file_path)


def replace_build_version(file_path):
    """
    Replace build version in build.gradle files.

    Args:
        file_path: path to build.gradle file

    Returns:
        None

    """
    newline = 'buildToolsVersion "{0}"'.format(BUILD_VERSION)
    tempfd, abs_path = tempfile.mkstemp()
    with open(abs_path, 'w') as new_file:
        if not os.path.isfile(file_path):
            return
        with open(file_path) as old_file:
            for line in old_file:
                result, count = re.subn(VERSION_PATTERN, newline, line)
                if count > 0:
                    LOG.debug('Replaced buildversion with %s', result)
                new_file.write(result)
    os.close(tempfd)
    os.remove(file_path)
    shutil.move(abs_path, file_path)
