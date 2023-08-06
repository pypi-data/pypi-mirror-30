"""
apk_launch performs various tasks for building Android projects.

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
import argparse
import re
import json
import shutil

import logging
import logging.handlers
from tqdm import tqdm

from apk_launch.utils import apk_utils
from apk_launch.utils import manifest_helper

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger(__name__)

# LINE_PACKAGE = re.compile('package=[\"\'](?P<package>[^\"]+)[\"\']')
# LINE_ACTIVITY = re.compile('')

ERROR_NOTINSTALLED = 3
BUILD_VERSION = '27.0.3'
VERSION_PATTERN = re.compile(r'buildToolsVersion "(?P<version>[\w\d\.]+)"')
ANT_ERROR_PATTERN = re.compile(r'(?P<fail>BUILD FAILED)')

SOURCE_DIRECTORY = '/media/yannes/research/benchmark_sources/'
APK_DIRECTORY = '/media/yannes/research/benchmark_apks/'


def parse_args():
    """
    Parse command line arguments.

    Args:
        None

    Returns:
        dict of command line args

    """
    parser = argparse.ArgumentParser(
        prog=__file__, description='Build and launch apk',
    )

    parser.add_argument('-s', '--stage',
                        help='Run stage(s)',
                        choices=['init', 'build', 'install', 'launch',
                                 'clean', 'uninstall', 'test', 'copy', 'reset',
                                 'all'],
                        # nargs = '+')
                        action='append')

    parser.add_argument('-d', '--dryrun',
                        help='Do not run the command(s)',
                        action='store_true',
                        default=False)

    parser.add_argument('-f', '--force',
                        help='Force rebuild of apk',
                        action='store_true')

    parser.add_argument('-a', '--activity',
                        help='Activity to launch')

    parser.add_argument('-n', '--appname', help='Application Name')

    parser.add_argument('-o', '--outdir',
                        help='Directory to store apks')

    parser.add_argument('-v', '--verbose',
                        help='Prints command output to screen',
                        action='store_true',
                        default=False)

    parser.add_argument('--outfile',
                        help='Prints results to json file',
                        default='apk_results.json')

    parser.add_argument('apps',
                        help='Filename of app root dirs or directory name')

    parser.add_argument('--list',
                        help='List all Applications',
                        action='store_true')

    parser.add_argument('-g', '--gradle',
                        help='Only list gradle files',
                        action='store_true')

    parser.add_argument('--listapks',
                        help='List all compiled debug apks',
                        action='store_true')

    parser.add_argument('--appsfile',
                        help='File to store applications directory list',
                        default='apps_list.txt')

    parser.add_argument('--logfile',
                        help='Log info to file')

    parser.add_argument('--count',
                        help='Max number of apps to build',
                        type=int)

    gradle_group = parser.add_mutually_exclusive_group()
    gradle_group.add_argument('--assume-gradle',
                              help='Assume all directories are gradle builds',
                              dest='assume_type',
                              action='store_true')
    gradle_group.add_argument('--dont-assume',
                              help='Do not assume directory build type',
                              dest='assume_type',
                              action='store_false')

    parser.set_defaults(assume_type=True)
    dat, _ = parser.parse_known_args()
    args = vars(dat)

    if args['verbose']:
        LOG.setLevel(logging.DEBUG)
        logging.getLogger('apk_utils').setLevel(logging.DEBUG)
        logging.getLogger('gradle_helper').setLevel(logging.DEBUG)
        logging.getLogger('manifest_helper').setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)
        logging.getLogger('apk_utils').setLevel(logging.INFO)
        logging.getLogger('gradle_helper').setLevel(logging.INFO)
        logging.getLogger('manifest_helper').setLevel(logging.INFO)

    if not args['stage']:
        args['stage'] = ['init', 'build']
    if 'all' in args['stage']:
        args['stage'] = ['init', 'build', 'install', 'launch']
    LOG.debug('Args: %s', args)
    return args


def parse_line(pattern, line):
    """
    Parse line for regular expression pattern.

    Args:
        pattern: regular expression pattern
        line: string to parse

    Returns:
        None if not in pattern, else dict of groups in pattern

    """
    match = re.match(pattern, line)
    return match.groupdict() if match else None


def handle_stage(args, rootdir, data, stage):
    """
    Run stage for apklaunch.

    Args:
        args: command line args
        rootdir: root directory
        data: manifest file data dict
        stage: stage to run

    Returns:
        True if successful, else False

    """
    if stage == 'init':
        args = apk_utils.init_directory(args, rootdir, data)
    elif stage == 'build':
        res = apk_utils.build(args, rootdir)
        if not res:
            LOG.info('BUILD FAILED')
            return False
        else:
            LOG.info('BUILD SUCCEEDED')
    elif stage == 'install':
        apk_utils.install(args, rootdir)
    elif stage == 'launch':
        apk_utils.launch(args, data)
    elif stage == 'test':
        apk_utils.test(args, rootdir)
    elif stage == 'uninstall':
        apk_utils.uninstall(args, rootdir)
    elif stage == 'copy':
        res = apk_utils.copyapk(args, rootdir, data)
        if not res:
            return False
    elif stage == 'clean':
        apk_utils.clean(args, rootdir)
    elif stage == 'reset':
        apk_utils.reset_directory(args, rootdir)
    return True


def apklaunch(args, rootdir, pbar):
    """
    Run apklaunch with args for a directory.

    Args:
        args: command line args
        rootdir: root directory
        pbar: progress bar

    Returns:
        None if not in completed, else dict of data in AndroidManifest

    Raises:
        TypeError if dirtype not detected
        ValueError if manifest could not be parsed

    """
    _, columns = os.popen('stty size', 'r').read().split()
    width = int(columns) - 60
    shortdir = '{text:>{len}}'.format(len=width,
                                      text='...' + rootdir[-width+3:]
                                      if len(rootdir) > width else rootdir)
    pbar.set_description('Processing {0}'.format(shortdir))
    LOG.debug('\n[apklaunch] Running on directory %s', rootdir)
    dirtype = 'gradle' if args['assume_type'] else apk_utils.get_project_type(rootdir)

    if not dirtype:
        raise TypeError

    args['dirtype'] = dirtype
    filename = apk_utils.find_manifest_file(rootdir)
    os.chdir(rootdir)

    data = manifest_helper.setup_manifest_data(rootdir, filename,
                                               search_activity=args.get('activity'),
                                               force=args.get('force'))
    LOG.debug('Data: %s', data)

    if args.get('dryrun'):
        raise StopIteration

    rootdir = os.getcwd()
    for stage in args['stage']:
        pbar.set_description('{0} {1}'.format(stage, shortdir))
        if not handle_stage(args, rootdir, data, stage):
            return None
    return data


def list_directories(topdir):
    """
    List all directories in topdir.

    Args:
        topdir: root directory

    Returns:
        list of directories

    """
    return [os.path.join(topdir, name)
            for name in os.listdir(topdir)
            if os.path.isdir(os.path.join(topdir, name))]


def get_all_directories(args):
    """
    List all directories.

    Args:
        args: command line args

    Returns:
        list of directories

    """
    if not os.path.isdir(args['apps']):
        raise ValueError('apps argument must be a directory when using --list')
    LOG.info('Fetching application directories from %s', args['apps'])
    dirs = []

    for dname in tqdm(list_directories(args['apps']), desc='Fetching directories'):
        dirs += list_directories(dname)

    LOG.debug('App dirs: %s', dirs)
    return dirs


MAXLEN = 40


def list_apps(args, dirs):
    """
    List all projects.

    Args:
        args: command line args
        dirs: directories to check

    Returns:
        dict of results

    """
    all_dirs = apk_utils.process_all_projects(dirs)

    for key in all_dirs:
        for dname in all_dirs[key]:
            LOG.info('%s directory: %s', key.title(), dname)

    LOG.info('%d Gradle Projects', len(all_dirs['gradle']))
    LOG.info('%d Non-Gradle Projects', len(all_dirs['nongradle']))
    LOG.info('%d Non-Android Projects', len(all_dirs['nonandroid']))

    file_prefix = '.'.join(args['appsfile'].split('.')[:-1])
    ext = args['appsfile'].split('.')[-1]
    for key in all_dirs:
        outfile = '{0}_{1}.{2}'.format(file_prefix, key, ext)

        if os.path.exists(outfile):
            LOG.info('File %s exists', outfile)
            choice = ''
            while choice.lower() not in ['y', 'n']:
                choice = raw_input('Replace file? [y/n] ')
            if choice.lower() == 'n':
                LOG.info('Not overwriting file %s', outfile)
                sys.exit(0)

        with open(outfile, 'w') as wfh:
            wfh.write('\n'.join(all_dirs[key]))
    return all_dirs


def get_apk_outpath(apk):
    """
    Get new path to copy apk to.

    Args:
        apk: path of apk to copy

    Returns:
        Full path to destination
        application package
        application category

    """
    prefix = apk.replace(SOURCE_DIRECTORY, '')
    LOG.debug('APK %s: prefix %s', apk, prefix)
    tokens = [t for t in prefix.split('/') if t]
    category = tokens[0]
    package = tokens[1]
    LOG.debug('%s: %s', category, apk)
    return '{0}/{1}'.format(APK_DIRECTORY, category), package, category


def list_apks(args, copyfiles=True):
    """
    List all apks.

    Args:
        args: command line args
        copyfiles: whether to copy found apks to outdir

    Returns:
        dict of results

    """
    apks = [a for a in apk_utils.parallel_apkexists(args['rootdir']) if a]
    LOG.info('Found %d apks', len(apks))
    lines = []
    for apk in tqdm(apks):
        if not apk:
            continue

        outpath, package, category = get_apk_outpath(apk)

        if copyfiles:
            if not os.path.exists(outpath):
                LOG.info('Creating directory: %s', outpath)
                os.makedirs(outpath)
            outfile = '{0}/{1}-debug.apk'.format(outpath, package)
            count = 1
            lines.append({'category': category, 'apk': apk})
            while os.path.exists(outfile):
                outfile = '{0}/{1}-debug-{2}.apk'.format(outpath, package, count)
                count += 1
                LOG.info('Apk %s exists. Trying again...', outfile)
            LOG.info('Copying %s to %s', apk, outfile)
            shutil.copyfile(apk, outfile)

    LOG.info('Writing log to %s', args['outfile'])
    with open(args['outfile'], 'w') as wfh:
        for line in lines:
            text = json.dumps(line, sort_keys=True)
            wfh.write(text + '\n')


# def get_app_list(args):
def get_app_list(appsinput, logfile=None, verbose=False):
    """
    Get list of apps from file or dir.

    Args:
        appsinput: file of apk list or directory to search
        logfile: log output to file
        verbose: debug logging if True

    Returns:
        List of application directories

    """
    rootdirs = []
    if os.path.isfile(appsinput):
        if logfile:
            handler = logging.FileHandler(logfile, mode='w')
            formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
            handler.setFormatter(formatter)
            LOG.handlers = [handler]

        LOG.setLevel(logging.DEBUG if verbose else logging.INFO)

        with open(appsinput, 'r') as rfh:
            for line in rfh.readlines():
                if line.strip():
                    rootdirs.append(line.strip())
    elif os.path.isdir(appsinput):
        rootdirs = [appsinput]
    return rootdirs


def main():
    """
    Script main loop.

    Args:
        None

    Returns:
        None

    """
    args = parse_args()

    if args['list']:
        dirs = get_all_directories(args)
        list_apps(args, dirs)
        return 0

    # args['rootdir'] = get_app_list(args)
    args['rootdir'] = get_app_list(args['apps'], args['logfile'], args['verbose'])

    if args['count']:
        cnt = args['count']
        if cnt > len(args['rootdir']) - 1:
            cnt = len(args['rootdir']) - 1
        args['rootdir'] = args['rootdir'][:cnt]

    LOG.debug('Root directories: %s', args['rootdir'])

    apkjson = {}
    apkjson['success'] = []
    apkjson['failure'] = []
    pbar = tqdm(args['rootdir'])

    if args['listapks']:
        LOG.info('Listing apks...')
        list_apks(args, copyfiles=not args['dryrun'])
        return 0

    maxlen = max([len(d) for d in args['rootdir']])
    maxlen = maxlen if maxlen < MAXLEN-3 else MAXLEN-3
    for rootdir in pbar:
        try:
            data = apklaunch(args, rootdir, pbar)
        except TypeError as terr:
            LOG.warn('TypeError: %s', terr)
            continue
        except ValueError as valerr:
            LOG.warn('ValueError: %s', valerr)
            continue

        if not data:
            apkjson['failure'].append(rootdir)
        else:
            LOG.debug('Sucessful task on: %s', data)
            apkjson['success'].append('{}/{}.apk'.format(args['outdir'], data['package']))

    if len(args['stage']) == 1 and 'reset' in args['stage']:
        LOG.info('Reset all directories')
        return 0

    if 'build' in args['stage'] and len(args['rootdir']) > 1:
        if args['outfile']:
            LOG.info('Writing log to %s', args['outfile'])
            with open(args['outfile'], 'w') as wfh:
                json.dump(apkjson, wfh, sort_keys=True, indent=4)

            apks = apkjson['success']
            outfile = '{}/ready_apks.json'.format(SOURCE_DIRECTORY)
            with open(outfile, 'w') as wfh:
                json.dump(apks, wfh, sort_keys=True)
