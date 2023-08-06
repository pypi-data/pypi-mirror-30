"""
apk_analyzer performs various tasks for analyzing apks.

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
import re
import argparse
import logging
from tqdm import tqdm

from apk_launch.utils import mycommand
from apk_launch.utils import mythreadcommand
from apk_launch.utils import tree_utils

logging.basicConfig(format='%(message)s', level=logging.INFO)
LOG = logging.getLogger(__name__)

ANDROID_SDK = (os.environ['ANDROID_SDK']
               if 'ANDROID_SDK' in os.environ
               else '{0}/android-sdk'.format(os.path.expanduser('~')))

# APKANALYZER = '{0}/tools_r25.2.5/bin/apkanalyzer'.format(ANDROID_SDK)
APKANALYZER = '{0}/tools.26.1.1/bin/apkanalyzer'.format(ANDROID_SDK)
if not os.path.isfile(APKANALYZER):
    APKANALYZER = '{0}/tools/bin/apkanalyzer'.format(ANDROID_SDK)

PACKAGE_PATTERN = re.compile(r'P\s*(?P<state>[xkrd])\s*(?P<defined>[\d]+)\s*'
                             r'(?P<referenced>[\d]+)\s*(?P<size>[\d]+)\s*'
                             r'(?P<name>[^\s]+)\s*(?P<extra>.*)')
CLASS_PATTERN = re.compile(r'C\s*(?P<state>[xkrd])\s*(?P<defined>[\d]+)\s*'
                           r'(?P<referenced>[\d]+)\s*(?P<size>[\d]+)\s*'
                           r'(?P<name>[^\s]+)')
METHOD_PATTERN = re.compile(r'M\s*(?P<state>[xkrd])\s*(?P<defined>[\d]+)\s*'
                            r'(?P<referenced>[\d]+)\s*(?P<size>[\d]+)\s*'
                            r'(?P<name>[^\s]+)\s*(?P<methodname>[^\(]+)'
                            r'\((?P<params>[^)]*)\)')
FIELD_PATTERN = re.compile(r'F\s*(?P<state>[xkrd])\s*(?P<defined>[\d]+)\s*'
                           r'(?P<referenced>[\d]+)\s*(?P<size>[\d]+)\s*'
                           r'(?P<name>[^\s]+)\s*(?P<data_type>[^\s]+)'
                           r'\s*(?P<field>.*)')

APK_PATTERN = re.compile(r'(?P<appname>[\w\d\_]+)_(?P<version>[\d\.]+)'
                         r'(\-(?P<extra>).+)?_APKTrunk')


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

    parser.add_argument('-o', '--outdir',
                        help='Directory to output apk data into',
                        default='.')

    parser.add_argument('-d', '--dryrun',
                        help='Do not save trees to file',
                        action='store_true')

    parser.add_argument('-v', '--verbose',
                        help='Print debug information',
                        action='store_true')

    parser.add_argument('-f', '--force',
                        help='Force overwriting of files',
                        action='store_true')

    parser.add_argument('-c', '--compare',
                        help='Compare app tree directories',
                        choices=['classes', 'fields', 'methods', 'packages'],
                        nargs='+',
                        default=['classes', 'packages'])

    parser.add_argument('--table',
                        help='Generate table from data',
                        action='store_true')

    dat, _ = parser.parse_known_args()
    dat = vars(dat)

    if dat['verbose']:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('tree_utils').setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)
        logging.getLogger('tree_utils').setLevel(logging.INFO)

    LOG.info('Args: %s', dat)

    return dat


def list_directories(topdir):
    """
    Get list of all directories.

    Args:
        topdir: root directory

    Returns:
        list of directories

    """
    _join = os.path.join
    _listdir = os.listdir
    _isdir = os.path.isdir
    return [_join(topdir, name) for name in _listdir(topdir)
            if _isdir(_join(topdir, name))]


def list_files(topdir, prefix=None, ext='.java'):
    """
    Get list of all files.

    Args:
        topdir: root directory
        prefix: file prefix to search for
        ext: file suffix to search for
    Returns:
        list of directories

    """
    file_list = []

    # Slight speedup
    _join = os.path.join
    for dirpath, _, files in os.walk(topdir):
        file_list += [_join(dirpath, f)
                      for f in files
                      if f.endswith(ext) and (prefix and f.startswith(prefix))]
    return file_list


def parse_line(pattern, line):
    """
    Match line against regular expression pattern.

    Args:
        pattern: regular expression pattern
        line: string to parse

    Returns:
        None if not in pattern, else dict of groups in pattern

    """
    data = re.match(pattern, line)
    if not data:
        return None
    return data.groupdict()


APK_SUMMARY = 0
APK_FILESIZE = 1
APK_DOWNLOADSIZE = 2
APK_FEATURES = 3
APK_VERSIONNAME = 4
APK_MINSDK = 5
APK_TARGETSDK = 6
APK_PERMISSIONS = 7
APK_APPLICATIONID = 8
APK_DEXPACKAGES = 9
APK_DEXCODE = 10
APK_DEXCODEMETHOD = 11

COMMAND_FORMATS = [
    '{apkanalyzer} apk summary {apk}',
    '{apkanalyzer} apk file-size {apk}',
    '{apkanalyzer} apk download-size {apk}',
    '{apkanalyzer} apk features {apk}',
    '{apkanalyzer} manifest version-name {apk}',
    '{apkanalyzer} manifest min-sdk {apk}',
    '{apkanalyzer} manifest target-sdk {apk}',
    '{apkanalyzer} manifest permissions {apk}',
    '{apkanalyzer} manifest application-id {apk}',
    '{apkanalyzer} dex packages {apk}',
    '{apkanalyzer} dex code {apk} --class {classname}'
    '{apkanalyzer} dex code {apk} --class {classname} --method {methodname}',
]


def apk_command(cmd_id, kwargs):
    """
    Run apk command in thread.

    Args:
        cmd_id: int id of cmd to run
        kwargs: args to pass to command

    Returns:
        None if not in pattern, else dict of groups in pattern

    """
    fmt = COMMAND_FORMATS[cmd_id]
    cmdstr = fmt.format(apkanalyzer=APKANALYZER, **kwargs)
    cmd = mythreadcommand.ThreadedCommand(cmdstr)
    return cmd


def apk_summary(apk):
    """
    Get apk summary.

    Args:
        apk: apk to sumarize

    Returns:
        (package, versionName, versionCode)

    """
    cmd = '{} apk summary {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log[0].split()


def apk_file_size(apk):
    """
    Get apk file size.

    Args:
        apk: apk to check

    Returns:
        file size

    """
    cmd = '{} apk file-size {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log[0]


def apk_download_size(apk):
    """
    Get apk download size.

    Args:
        apk: apk to check

    Returns:
        download size

    """
    cmd = '{} apk download-size {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log[0]


def apk_features(apk):
    """
    Get apk features.

    Args:
        apk: apk to check

    Returns:
        list of apk features

    """
    cmd = '{} apk features {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log


def manifest_version_name(apk):
    """
    Get apk manifest version name.

    Args:
        apk: apk to check

    Returns:
        string of manifest version name

    """
    cmd = '{} manifest version-name {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log[0]


def manifest_min_sdk(apk):
    """
    Get apk min sdk.

    Args:
        apk: apk to check

    Returns:
        min sdk num

    """
    cmd = '{} manifest min-sdk {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log[0]


def manifest_target_sdk(apk):
    """
    Get apk target sdk.

    Args:
        apk: apk to check

    Returns:
        target sdk num

    """
    cmd = '{} manifest target-sdk {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log[0]


def manifest_permissions(apk):
    """
    Get manifest permissions.

    Args:
        apk: apk to check

    Returns:
        list of permissions

    """
    cmd = '{} manifest permissions {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log


def manifest_application_id(apk):
    """
    Get manifest application-id.

    Args:
        apk: apk to check

    Returns:
        application id

    """
    cmd = '{} manifest application-id {}'.format(APKANALYZER, apk)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log[0]


def dex_packages(apk):
    """
    Get dex packages.

    Args:
        apk: apk to check

    Returns:
        list of dex packages

    """
    cmd = '{0} dex packages {1}'.format(APKANALYZER, apk)
    LOG.debug('Running: %s', cmd)
    proc = mycommand.Command(cmd)
    log = proc.run()
    return log


def dex_code(apk, classname, methodname=None):
    """
    Get dex code.

    Args:
        apk: apk to check
        classname: name of class to display
        methodname: name of method to display (defaults to None)

    Returns:
        list of dexcode output

    """
    cmd = '{} dex code {} --class {}'.format(APKANALYZER, apk, classname)
    if methodname:
        cmd = '{} --method {}'.format(cmd, methodname)
    proc = mycommand.Command(cmd)

    log = proc.run()
    return log


def fix_dex_package(item):
    """
    Cast dex package data to proper type.

    Args:
        item: dict of data

    Returns:
        dict of data

    """
    return {
        'name': item['name'],
        'defined': int(item['defined']),
        'referenced': int(item['referenced']),
        'size': int(item['size']),
        'state': str(item['state']),
    }


def fix_dex_class(item):
    """
    Cast dex class data to proper type.

    Args:
        item: dict of data

    Returns:
        dict of data

    """
    return {
        'name': item['name'],
        'defined': int(item['defined']),
        'referenced': int(item['referenced']),
        'size': int(item['size']),
        'state': str(item['state']),
    }


def fix_dex_method(item):
    """
    Cast dex method data to proper type.

    Args:
        item: dict of data

    Returns:
        dict of data

    """
    return {
        'name': item['name'],
        'defined': int(item['defined']),
        'referenced': int(item['referenced']),
        'methodname': str(item['methodname']),
        'params': str(item['params']),
        'size': int(item['size']),
        'state': str(item['state']),
    }


def fix_dex_field(item):
    """
    Cast dex field data to proper type.

    Args:
        item: dict of data

    Returns:
        dict of data

    """
    return {
        'name': item['name'],
        'defined': int(item['defined']),
        'referenced': int(item['referenced']),
        'field': str(item['field']),
        'data_type': str(item['data_type']),
        'size': int(item['size']),
        'state': str(item['state']),
    }


def parse_dex_packages(lines):
    """
    Parse dex packages output.

    Args:
        lines: list of input lines to parse

    Returns:
        classes: list of parsed class lines
        fields: list of parsed field lines
        methods: list of parsed method lines
        packages: list of parsed package lines

    """
    packages = []
    methods = []
    fields = []
    classes = []
    for line in tqdm(lines, leave=False):
        item = parse_line(PACKAGE_PATTERN, line)
        if item:
            # packages.append(fix_dex_package(item))
            packages.append(item)
            continue
        item = parse_line(CLASS_PATTERN, line)
        if item:
            # classes.append(fix_dex_class(item))
            classes.append(item)
            continue
        item = parse_line(METHOD_PATTERN, line)
        if item:
            # methods.append(fix_dex_method(item))
            methods.append(item)
            continue
        item = parse_line(FIELD_PATTERN, line)
        if item:
            # fields.append(fix_dex_field(item))
            fields.append(item)
            continue
    return classes, fields, methods, packages


# pylint: disable=dangerous-default-value
def parse_apk_data(apk, compare=['classes', 'packages', 'fields', 'methods']):
    """
    Parse apk data.

    Args:
        apk: apk to parse
        compare: only parse if ('classes', 'packages', 'fields', 'methods') in list

    Returns:
        classes: list of parsed class lines
        fields: list of parsed field lines
        methods: list of parsed method lines
        packages: list of parsed package lines

    """
    log = dex_packages(apk)
    packages = []
    methods = []
    fields = []
    classes = []
    classes, fields, methods, packages = parse_dex_packages(log)
    LOG.debug('%s classes', len(classes))
    LOG.debug('%s fields', len(fields))
    LOG.debug('%s methods', len(methods))
    LOG.debug('%s packages', len(packages))

    if 'classes' not in compare:
        classes = []
    if 'fields' not in compare:
        fields = []
    if 'methods' not in compare:
        methods = []
    if 'packages' not in compare:
        packages = []

    return classes, fields, methods, packages


def match_state(items, state):
    """
    Check if state matches.

    Args:
        items: list of items

    Returns:
        list of matching items

    """
    return [item for item in items if item.get('state') == state]


def read_app_data(inputdir, choice=None):
    """
    Read all tree files from directory.

    Args:
        inputdir: list of input lines to parse
        choice: prefix to search for

    Returns:
        list of trees

    """
    trees = []
    files = list_files(inputdir, prefix=choice, ext='.dat')
    for fname in tqdm(files, leave=False):
        LOG.debug('Reading tree from %s', fname)
        tree = tree_utils.read_treefile(fname)
        LOG.debug('Read tree from %s', fname)
        trees.append(tree)
    return trees


def extract_name(text, choice):
    """
    Extract name from text.

    Args:
        text: text containing name
        choice: one of (classes, fields, methods, packages)

    Returns:
        string of name

    """
    fname = '.'.join(text.split('/')[-1].split('.')[:-1])
    name = fname.replace(choice + '_', '')
    return name


def make_filename(choice, name):
    """
    Make tree filename from choice.

    Args:
        choice: one of (classes, fields, methods, packages)
        name: name of item

    Returns:
        string of filename

    """
    return '{0}_{1}.dat'.format(choice, name)


def list_choice_types(inputdir, choice):
    """
    List all files matching choice in directory.

    Args:
        inputdir: root directory
        choice: one of (classes, fields, methods, packages)

    Returns:
        list of matching files

    """
    files = list_files(inputdir, prefix=choice, ext='.dat')

    names = sorted(list(set([extract_name(f, choice) for f in files])))
    LOG.debug('%d %s:%s', len(names), choice, names)
    return names


def list_choice_files(inputdir, choice):
    """
    List all files matching choice in directory.

    Args:
        inputdir: root directory
        choice: one of (classes, fields, methods, packages)

    Returns:
        list of matching files

    """
    names = list_choice_types(inputdir, choice)
    all_files = {}
    for name in names:
        all_files[name] = list_files(inputdir, prefix='{0}_{1}'.format(choice, name), ext='.dat')

    LOG.debug('All %s files (%d):', choice, len(all_files))
    for name in all_files:
        LOG.debug('\t%s (%s): %s', name, len(all_files[name]), ', '.join(all_files[name]))
    return all_files


def read_all_from_directory(inputdir, choice=None, dryrun=False):
    """
    Read all tree files in directory.

    Args:
        inputdir: root directory
        choice: one of (classes, fields, methods, packages)

    Returns:
        list of trees

    """
    all_files = list_choice_files(inputdir, choice)
    apk_trees = {}

    if dryrun:
        sys.exit(0)

    names = [name for name in all_files]
    for name in tqdm(names):
        apk_trees[name] = []
        for fname in tqdm(all_files[name], leave=False):
            apk_trees[name].append(tree_utils.read_treefile(fname))

    for apk in apk_trees:
        LOG.debug(apk)
        for tree in apk_trees[apk]:
            LOG.debug('\t%s', tree)

    all_trees = [apk_trees[apk] for apk in apk_trees]
    for tree1, tree2 in zip(tqdm(all_trees[:-1]), tqdm(all_trees[1:])):
        tree_utils.union_trees(tree1, tree2)

    return apk_trees


def is_package_parent(data, packagename):
    """
    Check if packagename in data.

    Args:
        data: dict of data
        packagename: name of package

    Returns:
        True if found, else False

    """
    for key in data:
        if key.startswith(packagename):
            return True
    return False


def generate_table(args):
    """
    Generate latex table.

    Args:
        args: command line args

    Returns:
        None

    """
    # pylint: disable=too-many-function-args
    # classes, fields, methods, packages = dex_packages(args, args['input'])
    _, _, _, packages = dex_packages(args, args['input'])
    packages = sorted(packages, key=lambda x: x['name'].count('.'), reverse=True)

    data = {}
    _inpackage = is_package_parent
    for package in tqdm(packages):
        name = package.get('name')

        inname = ('android.support' in name or name.startswith('edu'))
        if not _inpackage(data, name) and inname:
            LOG.debug('Package: %s', package)
            data[name] = package

    data = sorted([data[key] for key in data], key=lambda x: x['name'])
    LOG.info('Generating table for %s', args['input'])

    lines = ['\\begin{table}[]']
    lines.append('\\begin{tabular}{|c|c|c|c|c|} \\\\\n\\hline')
    lines.append('\\multicolumn{1}{|c|}{Package} & '
                 '\\multicolumn{1}{c|}{Defined Methods} & '
                 '\\multicolumn{1}{c|}{Referenced Methods} & '
                 '\\multicolumn{1}{c|}{Size (B)} \\\\')

    for row in data:
        line = ('{0} & {1} & {2} & {3} \\\\'
                .format(row['name'], row['defined'], row['referenced'], row['size']))
        lines.append(line)

    lines.append('\\end{tabular}\n\\end{table}')
    LOG.info('%s', '\n'.join(lines))


def main():
    """
    Script main loop.

    Args:
        None

    Returns:
        0 if success, else > 0

    """
    args = parse_args()

    if args['table']:
        args['compare'] = ['packages']
        generate_table(args)
        return 0

    if args['input'].endswith('.apk'):
        baseapk = args['input'].split('/')[-1]
        path = '{}/{}'.format(args['outdir'], '.'.join(baseapk.split('.')[:-1]))
        if os.path.exists(path) and not args['force']:
            LOG.info('Already parsed %s into %s. Quitting', args['input'], path)
            return 0

        classes, fields, methods, packages = parse_apk_data(args['input'], args['compare'])
        class_trees, field_trees, method_trees, package_trees = tree_utils.organize_as_trees(
            classes, fields, methods, packages)

        if args['verbose']:
            tree_utils.print_trees(class_trees, field_trees, method_trees, package_trees)

        if args['dryrun']:
            return 0

        if args['outdir']:
            data = {
                'classes': class_trees,
                'fields': field_trees,
                'methods': method_trees,
                'packages': package_trees,
            }
            LOG.info('Saving %s trees', args['input'])
            tree_utils.save_all_trees(args, data)
    elif args['input'].endswith('.tree.gz'):
        tree = tree_utils.read_treefile(args['input'])
        LOG.debug('Tree dir: %s', dir(tree))
        root = tree.root
        LOG.info('Tree root %s: %s', type(root), root)
        for node in tree.all_nodes():
            LOG.info('node %s: %s', type(node), node)

        tree.show()
    elif os.path.isdir(args['input']):
        if not args['compare']:
            LOG.error('Error: missing -c flag')
            return 1
        read_all_from_directory(args['input'], choice=args['compare'], dryrun=args['dryrun'])
        return 0
    else:
        LOG.error('Error: invalid input "%s"', args['input'])
        return 1
