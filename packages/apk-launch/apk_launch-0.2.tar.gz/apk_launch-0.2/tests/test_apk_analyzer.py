"""
    Performs various tests on apk_analyzer.

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
from unittest import TestCase

import logging
import os

# pylint: disable=import-error
from apk_launch.apk_analyzer import apk_analyzer


class TestCmd(TestCase):
    """Performs various tests on apk_analyzer."""

    def test_parse_args(self):
        """
        Test basic apk_analyzer main (no args).

        """
        with self.assertRaises(SystemExit) as catch:
            apk_analyzer.main()

        self.assertEqual(catch.exception.code, 2)

    def test_parse_apk_data(self):
        """
        Test apk_analyzer with apk file and packages.

        """
        logging.getLogger('apk_analyzer').setLevel(logging.DEBUG)
        logging.getLogger('mycommand').setLevel(logging.DEBUG)
        apk = '{0}/tests/hashmap-armeabi-v7a-debug.apk'.format(os.getcwd())
        category = ['classes', 'fields', 'methods', 'packages']
        print 'Analyzing {0}'.format(apk)
        classes, fields, methods, packages = apk_analyzer.parse_apk_data(apk, category)

        print 'Num classes: ', len(classes)
        print 'Num fields: ', len(fields)
        print 'Num methods: ', len(methods)
        print 'Num packages: ', len(packages)

        self.assertEqual(len(classes), 2137)
        self.assertEqual(len(fields), 10382)
        self.assertEqual(len(methods), 17392)
        self.assertEqual(len(packages), 122)
