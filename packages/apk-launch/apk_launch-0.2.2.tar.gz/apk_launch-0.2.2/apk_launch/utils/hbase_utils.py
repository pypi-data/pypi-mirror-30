"""
hbase_utils is a helper class for the posting to hbase.

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

import sys
import argparse
import hashlib
import socket
import logging

from contextlib import contextmanager
import happybase
from happybase.pool import ConnectionPool, TException, socket

# pylint: disable=import-error
from thrift.Thrift import TException

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger(__name__)

HBASE_APK_TABLE = {
    'apk_data': dict(),
    'dex_data': dict(),
    'permissions': dict(),
}

APK_TABLE = 'apk'
APK_TABLE_CF = 'cf1'
CLASS_TABLE = 'apk_class'
CLASS_TABLE_CF = 'cf1'
FIELD_TABLE = 'apk_field'
FIELD_TABLE_CF = 'cf1'
METHOD_TABLE = 'apk_method'
METHOD_TABLE_CF = 'cf1'


def parse_args():
    """
    Parse command line arguments.

    Args:
        None

    Returns:
        dict of command line args

    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        description='Run commands on hbase',
    )

    parser.add_argument('-v', '--verbose',
                        help='Print debug information',
                        action='store_true')

    args, _ = parser.parse_known_args()
    args = vars(args)

    if args['verbose']:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)

    LOG.debug('Args: %s', args)
    return args


def create_apk_table(conn):
    """
    Create apk table for hbase.

    Args:
        conn: hbase connection

    Returns:
        True if successful, else False

    """
    if not conn:
        return False
    if 'apk' in conn.tables():
        LOG.info('apks table already exists. Skipping')
        return True
    conn.create_table('apk', HBASE_APK_TABLE)
    return True


def add_column_family(data, column_family):
    """
    Add family column to dictionary.

    Args:
        data: dictionary
        column_family: name of column family

    Returns:
        new dict with data in column family

    """
    items = dict()
    for key in data:
        new_key = '{}:{}'.format(column_family, key)
        items[new_key] = data[key]
    return items


def nested_to_row(package, data, column_family):
    """
    Generate row with package as key.

    Args:
        package: application package
        data: application data
        column_family: name of column to store in

    Returns:
        key of where data is stored
        dict containing reformatted data

    """
    key = '{}.{}'.format(package, hashlib.md5(package).hexdigest())
    data['package'] = package

    # Slight speedup
    _add_column_family = add_column_family
    return key, _add_column_family(data, column_family)


# pylint: disable=too-many-arguments
def store_nested_data(conn, table_name, table_key, data, data_key, table_cf):
    """
    Store data to hbase table.

    Args:
        conn: hbase connection
        table_name: name of table
        table_key: table key
        data: data to store in table
        data_key: key for this data
        table_cf: column family for this data

    Returns:
        None

    """
    table = conn.table(table_name)
    LOG.debug('Storing %s[%s]', table_key, data_key)
    with table.batch() as batch:
        for item in data[data_key]:
            row_key, row_data = nested_to_row(table_key, item, table_cf)
            batch.put(row_key, row_data)


def store_apk_data(conn, data):
    """
    Store apk to hbase table.

    Args:
        conn: hbase connection
        data: data to store in table

    Returns:
        None

    """
    apk_table = conn.table(APK_TABLE)
    key = data['package']

    apk_keys = ['category', 'version_code', 'file_size',
                'download_size', 'min_sdk', 'target_sdk']
    apk_data = add_column_family({k: data[k] for k in apk_keys}, APK_TABLE_CF)
    LOG.info('Storing apk[%s]: %s', key, apk_data)
    # apk_table.put(key, apk_data)
    for k in apk_data:
        LOG.debug('Putting: %s:%s', k, apk_data[k])
        apk_table.put(key, {k: apk_data[k]})

    items = [
        (CLASS_TABLE, 'classes', CLASS_TABLE_CF),
        (FIELD_TABLE, 'fields', FIELD_TABLE_CF),
        (METHOD_TABLE, 'methods', METHOD_TABLE_CF),
    ]

    for table_name, data_key, cfname in items:
        store_nested_data(conn, table_name, key, data, data_key, cfname)


class AutoRetryPool(ConnectionPool):
    # pylint: disable=too-few-public-methods
    """Connection pool which does its best to ensure open connections.

    May impose some overhead (ie not good for low-latency stuff) but should
    increase reliability of getting a working, open connection when needed

    Based on post by gorlins from https://github.com/wbolster/happybase/issues/133

    """

    def __init__(self, size, retries=5, **kwargs):
        """
        Initialize connection pool.

        Args:
            size: number of connections
            retries: number of retries (defaults to 5)
            kwargs: remaining args

        Returns:
            None

        """
        self.retries = retries
        super(AutoRetryPool, self).__init__(size, **kwargs)

    @contextmanager
    def connection(self, timeout=None):
        """
        Start connection.

        Args:
            timeout: assign timeout to connection (defaults to None)

        Returns:
            None

        """
        attempts = 0
        opened = False
        while True:
            try:
                with super(AutoRetryPool, self).connection(timeout=timeout) as conn:
                    # Make an actual call to ensure
                    _ = conn.tables()
                    opened = True
                    yield conn
                return

            except (TException, socket.error):
                # These trigger refreshed connections in parent
                if opened:
                    # aka the failure was inside the yield, can't fix
                    raise

                attempts += 1
                # print 'Replacing connection, attempt', attempts
                if attempts >= self.retries:
                    raise

    def _return_connection(self, connection):
        """
        Return connection.

        Args:
            connection: hbase connection

        Returns:
            connection

        """
        # Don't leave idling connections around - too easy to timeout before use
        connection.close()
        return super(AutoRetryPool, self)._return_connection(connection)


def main():
    """
    Script main loop.

    Args:
        None

    Returns:
        None

    """
    parse_args()
    conn = happybase.Connection('localhost')
    if not create_apk_table(conn):
        LOG.error('Error creating table')
        sys.exit(1)
    LOG.info('Tables: %s', conn.tables())


if __name__ == '__main__':
    main()
