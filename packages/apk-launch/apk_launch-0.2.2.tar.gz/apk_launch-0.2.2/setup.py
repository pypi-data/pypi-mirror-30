"""
Setup for apk_launch project
"""

import distutils.cmd
import distutils.log
import subprocess
import os
import setuptools
from glob import glob

VERSION = '0.2.2'

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

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
    # package_dir={'': 'apk_launch'},
    # py_modules=['src/apk_analyzer', 'src/apk_launch', 'src/apk_stats', 'src/utils'],
    include_package_data=True,
    version=VERSION,
    description='Tools for performing various tasks on Android projects',
    long_description=open('README.md').read(),
    author='Zach Yannes',
    author_email='zachyannes@gmail.com',
    url='https://github.com/Zachout',
    download_url='https://github.com/Zachout/apk_launch/archive/0.2.tar.gz',
    keywords=['android', 'build', 'analyze', 'dex'],
    classifiers=[],
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'pylint'],
    # cmdclass={
    #     'pylint': PylintCommand,
    # },
    # entry_points = {
    #     'console_scripts': [
    #         'apk_analyzer=apk_launch.apk_analyzer.apkanalyzer:main',
    #         'apk_launch=apk_launch.apk_launch.apklaunch:main',
    #         'apk_stats=apk_launch.apk_stats.apkstats:main',
    #     ],
    # },
    scripts=['scripts/apkanalyzer', 'scripts/apklaunch', 'scripts/apkstats']
)
