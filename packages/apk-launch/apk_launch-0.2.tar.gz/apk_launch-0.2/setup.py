"""
Setup for apk_launch project
"""

import distutils.cmd
import distutils.log
import subprocess
import os
import setuptools
from glob import glob

VERSION = '0.2'

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


'''
class PylintCommand(distutils.cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run Pylint on Python source files'
    user_options = [
        # The format is (long option, short option, description).
        ('pylint-rcfile=', None, 'path to Pylint config file'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.pylint_rcfile = '.pylintrc'

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
            assert os.path.exists(self.pylint_rcfile), (
                'Pylint config file %s does not exist.' % self.pylint_rcfile)

    def run(self):
        """Run command."""
        command = ['/usr/bin/pylint']
        if self.pylint_rcfile:
            command.append('--rcfile=%s' % self.pylint_rcfile)
        # command.append(os.getcwd())
        command.append('src')
        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        subprocess.check_call(command)
'''

'''
# Test dependencies
with open(os.path.join(os.path.dirname(__file__), 'tests', 'requirements.txt')) as f:
    tests_requires = f.read().split()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    install_requires = f.read().split()
'''

setuptools.setup(
    name='apk_launch',
    packages=find_packages(exclude=('tests', 'docs')),
    license=open('LICENSE.txt').read(),
    package_dir={
        'apk_launch': 'apk_launch',
        'utils': 'utils',
    },
    # py_modules=['src/apk_analyzer', 'src/apk_launch', 'src/apk_stats', 'src/utils'],
    include_package_data=True,
    version=VERSION,
    description='Tools for performing various tasks on Android projects',
    long_description=open('README.md').read(),
    author='Zach Yannes',
    author_email='zachyannes@gmail.com',
    url='https://github.com/Zachout',
    download_url='https://github.com/Zachout/apk_launch/archive/0.1.tar.gz',
    keywords=['android', 'build', 'analyze', 'dex'],
    classifiers=[],
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'pylint'],
    # cmdclass={
    #     'pylint': PylintCommand,
    # },
    scripts=[
        'apk_launch/apkanalyzer.py',
        'apk_launch/apklaunch.py',
        'apk_launch/apkstats.py',
    ],
    # scripts=['src/apk_analyzer/apk_analyzer.py', 'src/apk_launch/apk_launch.py', 'src/apk_stats/apk_stats.py']
)
