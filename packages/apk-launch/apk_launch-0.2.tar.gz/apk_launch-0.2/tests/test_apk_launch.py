"""
    Performs various tests on apk_launch.

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

# pylint: disable=import-error
from apk_launch.apk_launch import apk_launch


class TestCmd(TestCase):
    """Performs various tests on apk_launch."""

    def test_parse_args(self):
        """
        Test basic apk_launch main (no args).

        """
        with self.assertRaises(SystemExit) as catch:
            apk_launch.main()

        self.assertEqual(catch.exception.code, 2)

    def test_get_app_list(self):
        """
        Test apk_launch.get_app_list with directory.

        """
        appsinput = '.'
        apps_list = apk_launch.get_app_list(appsinput)

        print 'Apps list: ', apps_list
        self.assertEqual(len(apps_list), 1)
