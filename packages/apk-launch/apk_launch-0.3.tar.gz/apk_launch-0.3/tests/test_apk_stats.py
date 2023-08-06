"""
    Performs various tests on apk_stats.

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
from apk_launch.apk_stats import apkstats


class TestCmd(TestCase):
    """Performs various tests on apk_stats."""

    def test_parse_args(self):
        """
        Test basic apk_stats main (no args).

        """
        with self.assertRaises(SystemExit) as catch:
            apkstats.main()

        self.assertEqual(catch.exception.code, 2)

    def test_apk_stats(self):
        """
        Test apk_launch.get_app_list with directory.

        """
        apk = ('hashmap-armeabi-v7a-debug.apk')
        category = ['classes', 'fields', 'methods', 'packages']
        output = apkstats.apk_stats(apk, category)
        self.assertNotEqual(output, {})
