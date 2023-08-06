#!/usr/bin/env python
"""
apk_stats calculates statistics about apks.

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
import json
from collections import OrderedDict
import logging
import pprint

from tqdm import tqdm
import happybase

from apk_analyzer import apk_analyzer
from utils import hbase_utils

logging.basicConfig(level=logging.INFO, format='%(message)s')
# logging.basicConfig()
LOG = logging.getLogger(__name__)

CATEGORIES = [
    'Connectivity', 'Development', 'Games', 'Graphics', 'Internet', 'Money',
    'Multimedia', 'Navigation', 'Phone_%26_SMS', 'Reading', 'Science_%26_Education',
    'Security', 'Sports_%26_Health', 'System', 'Theming', 'Time', 'Writing'
]

CMD_IDS = [
    ('summary', apk_analyzer.APK_SUMMARY),
    ('file_size', apk_analyzer.APK_FILESIZE),
    ('download_size', apk_analyzer.APK_DOWNLOADSIZE),
    ('min_sdk', apk_analyzer.APK_MINSDK),
    ('target_sdk', apk_analyzer.APK_TARGETSDK),
    ('permissions', apk_analyzer.APK_PERMISSIONS),
    ('packages', apk_analyzer.APK_DEXPACKAGES),
]


def valid_category(cat):
    """
    Calculate if category is valid.

    Args:
        cat: category to check

    Returns:
        value of category if found

    Raises:
        ValueError if not found

    """
    try:
        idx = CATEGORIES.index(cat)
        return CATEGORIES[idx]
    except ValueError:
        msg = "Not a valid category: '{0}'.".format(cat)
        LOG.error(msg)
        raise ValueError


def parse_args():
    """
    Parse command line arguments.

    Args:
        None

    Returns:
        dict of command line args

    """
    parser = argparse.ArgumentParser(
        prog='PROG',
        description='Analyze Android apk file',
    )

    parser.add_argument('input',
                        help='Input (apk or directory)')

    parser.add_argument('--category',
                        help='Application category',
                        type=valid_category)

    parser.add_argument('-o', '--outdir',
                        help='Directory to output apk data into',
                        default='.')

    parser.add_argument('-d', '--dryrun',
                        help='Do not save trees to file',
                        action='store_true')

    parser.add_argument('-v', '--verbose',
                        help='Print debug information',
                        action='store_true')

    parser.add_argument('-s', '--store',
                        help='Store data to hbase',
                        action='store_true')

    parser.add_argument('--logfile',
                        help='Log debug info to file',
                        default='apk_stats.log')

    args, _ = parser.parse_known_args()
    args = vars(args)

    if args['verbose']:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('hbase_utils').setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)

    LOG.info('Args: %s', args)
    return args


def count_states(items):
    """
    Count number of states in all items.

    Args:
        items: list of either (classes, fields, methods, packages)

    Returns:
        OrderedDict with count of defined/referenced

    """
    defined = apk_analyzer.match_state(items, 'd')
    referenced = apk_analyzer.match_state(items, 'r')

    return OrderedDict([
        ('defined', len(defined)),
        ('referenced', len(referenced)),
    ])


def print_dict(data, depth=0, singleline=False):
    """
    Print dictionary.

    Args:
        data: data to print
        depth: current depth of dict (defaults to 0)
        singleline: whether to print on one line (defaults to False)

    Returns:
        None

    """
    if singleline:
        text = ', '.join(['{0}: {1}'.format(key, data[key]) for key in data])
        LOG.info('%s', '{indent}{text}'.format(indent=' ' * depth, text=text))
        return

    maxwidth = max([len(key) for key in data])
    for key in data:
        if isinstance(data[key], dict):
            output = '{indent}{text:>{width}}:'.format(indent=' ' * depth,
                                                       text=key, width=maxwidth)
            LOG.info('%s', output)
            print_dict(data[key], depth=depth + maxwidth + 1)
        else:
            output = '{indent}{text:>{width}}: {val}'.format(indent=' ' * depth,
                                                             text=key, width=maxwidth,
                                                             val=data[key])
            LOG.info('%s', output)


def apk_stats(apkfile, category):
    """
    Calculate statistics for apk file.

    Args:
        apkfile: file to analyze
        category: category of application see CATEGORIES

    Returns:
        json object of stats

    """
    cmds = []
    for cmd_str, cmd_id in CMD_IDS:
        cmd = apk_analyzer.apk_command(cmd_id, {'apk': apkfile})
        cmd.start()
        cmds.append((cmd_str, cmd))

    items = OrderedDict()
    items['category'] = category
    for cmd_str, cmd in tqdm(cmds, leave=False):
        LOG.debug('Joining %s', cmd_str)
        cmd.join()
        log = cmd.get_log()
        if cmd_str == 'packages':
            # lines = cmd.wait().split('\n')
            classes, fields, methods, _ = apk_analyzer.parse_dex_packages(log.split('\n'))
            items['classes'] = classes  # count_states(classes)
            items['fields'] = fields  # count_states(fields)
            items['methods'] = methods  # count_states(methods)
            # items['packages'] = count_states(packages)
        elif cmd_str == 'summary':
            tokens = log.split()
            items['package'] = tokens[0]
            items['version_code'] = tokens[1]  # int(tokens[1])
            if len(tokens) >= 3:
                items['version_name'] = tokens[2]
        elif cmd_str in ['file_size', 'download_size', 'min_sdk', 'target_sdk']:
            items[cmd_str] = log.strip()
        else:
            items[cmd_str] = [l.strip() for l in log.split('\n') if l]

    text = json.dumps(items, sort_keys=False)
    return json.loads(text)


def main():
    """
    Script main loop.

    Args:
        args: command line args

    Returns:
        none

    """
    args = parse_args()
    if not args['input']:
        line = sys.stdin.readline()
        LOG.info('Read in "%s"', line)
        args['input'] = line.rstrip()

    tokens = args['input'].split('/')
    category = valid_category(tokens[-2])
    # apkname = tokens[-1]
    if args['input'].endswith('.apk'):
        data = apk_stats(args['input'], category)
        LOG.debug(pprint.pformat(data, indent=4))
        if args['store']:
            conn = happybase.Connection('localhost')
            hbase_utils.store_apk_data(conn, data)
    else:
        LOG.error('Error: invalid input "%s"', args['input'])


if __name__ == '__main__':
    main()
