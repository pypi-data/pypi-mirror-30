"""
apk_utils contains helper methods for dealing with apks.

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
import re
import logging
import shutil

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import scandir

from apk_launch.utils import gradle_helper
from apk_launch.utils import mycommand

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger(__name__)
# LOG.setLevel(logging.INFO)

DEFAULT_ERROR_PATTERN = re.compile(r'(?P<fail>FAILED)')
ANT_ERROR_PATTERN = re.compile(r'(?P<fail>BUILD FAILED)')

TASK_TIMEOUT = 5 * 60  # 5 minutes


def find_files_recursive(rootdir, filename, parent=None):
    """
    Find files recursively matching filename.

    Args:
        rootdir: root directory to search
        filename: name of file to search for
        parent: only return files with parent as parent dir (defaults to None)

    Returns:
        List of files matching search parameters

    """
    found = []
    # LOG.debug('Recursively searching {} for {}, {}'.format(rootdir, filename, parent))
    for root, subdir, files in scandir.walk(rootdir):
        files = [f for f in files if f[0] != '.']
        subdir[:] = [d for d in subdir if d[0] != '.']
        # LOG.debug('Root {}, Subdirectories: {}'.format(root, subdir))
        if parent and not root.endswith(parent):
            continue

        # LOG.debug('Root {}, files: {}'.format(root, files))
        if filename in files:
            # return '{}/{}'.format(root, filename)
            # LOG.debug('Found {} in {}/{}'.format(filename, root, filename))
            path = os.path.abspath(os.path.join(root, filename))
            found.append(path)

    return sorted(found)


def find_file_pattern_recursive(rootdir, pattern, parent=None):
    """
    Find files recursively matching pattern (re).

    Args:
        rootdir: root directory to search
        pattern: name of file to search for
        parent: only return files with parent as parent dir (defaults to None)

    Returns:
        List of files matching search parameters

    """
    found = []
    # LOG.debug('Recursively searching {} for {}'.format(rootdir, pattern))
    for root, _, files in scandir.walk(rootdir):
        # LOG.debug('Root {}, Subdirectories: {}'.format(root, subdir))
        if parent and not root.endswith(parent):
            continue
        for filename in files:
            if pattern in filename:
                LOG.debug('Found %s in %s/%s', filename, root, pattern)
                path = os.path.abspath(os.path.join(root, filename))
                found.append(path)

    return sorted(found)


def find_directory_recursive(rootdir, pattern):
    """
    Find directories recursively matching pattern.

    Args:
        rootdir: root directory to search
        filename: name of file to search for
        parent: only return files with parent as parent dir (defaults to None)

    Returns:
        List of files matching search parameters

    """
    _join = os.path.join
    _walk = scandir.walk
    _abspath = os.path.abspath
    _match = re.match
    return [_abspath(_join(root, dname))
            for root, subdir, _ in _walk(rootdir)
            for dname in subdir if _match(pattern, _abspath(_join(root, dname)))]


def find_file_pattern_fast(rootdir, pattern):
    """
    Find files recursively matching pattern.

    Args:
        rootdir: root directory to search
        filename: name of file to search for
        parent: only return files with parent as parent dir (defaults to None)

    Returns:
        List of files matching search parameters

    """
    found = []

    # Small speedups
    _abspath = os.path.abspath
    _join = os.path.join
    _match = re.match
    for root, _, files in scandir.walk(rootdir):
        # LOG.debug('Matching files: {}'.format(files))
        found += [_abspath(_join(root, fname)) for fname in files if _match(pattern, fname)]
    return found


def get_parent_directory(path):
    """
    Get parent directory.

    Args:
        path: total path

    Returns:
        The parent directory

    """
    parent = os.path.abspath(os.path.join(path, os.pardir))
    return parent.split('/')[-1]


def find_manifest_file(rootdir):
    """
    Find AndroidManifest.xml recursively.

    Args:
        rootdir: root directory to search

    Returns:
        path to AndroidManifest.xml

    """
    files = find_files_recursive(rootdir, 'AndroidManifest.xml')
    if not files:
        return None
    if len(files) == 1:
        return files[0]

    files = [fname for fname in files if 'build' not in fname.split('/')]

    # Small speedup
    _getparent = get_parent_directory
    for fname in files:
        if _getparent(fname) == 'main':
            return fname
    return files[0]


# Can either be: gradle, ant, or maven
def get_project_type(rootdir):
    """
    Check if directory is a gradle project.

    Args:
        rootdir: root directory to check

    Returns:
        True if gradle project else False

    """
    files = find_files_recursive(rootdir, 'gradlew')  # , parent = 'app')
    if files:
        return 'gradle'
    files = find_files_recursive(rootdir, 'build.xml')
    if files:
        LOG.debug('Got maven project: files %s', files)
        return 'maven'
    files = find_files_recursive(rootdir, 'Android.mk')
    if files:
        return 'android'

    LOG.error('Error: project %s is not gradle, maven, or android', rootdir)
    return 'gradle'


def is_gradle_project(rootdir):
    """
    Check if directory is a gradle project.

    Args:
        rootdir: root directory to check

    Returns:
        True if gradle project else False

    """
    gradlefile = 'gradlew'  # 'build.gradle'
    files = find_files_recursive(rootdir, gradlefile)  # , parent = 'app')
    if not files:
        return None

    return [os.path.abspath(os.path.join(fname, os.pardir))
            for fname in files if get_parent_directory(fname) != gradlefile]


def is_android_project(rootdir):
    """
    Check if directory is an Android project.

    Args:
        rootdir: root directory to check

    Returns:
        True if Android project else False

    """
    filename = find_manifest_file(rootdir)
    return True if filename else False


MAXLEN = 40


def process_all_projects(dirs):
    """
    Process all directories in rootdir to determine project type.

    Args:
        dirs: list of directories to search

    Returns:
        dict of results where key is (gradle, nongradle, nonandroid)

    """
    all_dirs = {}
    all_dirs['gradle'] = []
    all_dirs['nongradle'] = []
    all_dirs['nonandroid'] = []

    maxlen = max([len(dname) for dname in dirs])
    maxlen = maxlen if maxlen < MAXLEN-3 else MAXLEN-3
    pbar = tqdm(dirs, desc='Processing projects')
    for dname in pbar:
        text = '...' + dname[-maxlen:]
        if len(text) == MAXLEN-3:
            text = '...' + text
        pbar.set_description('Processing {text:{len}}'.format(len=maxlen, text=text))
        subprojs = is_gradle_project(dname)
        if not subprojs:
            if is_android_project(dname):
                all_dirs['nongradle'].append(dname)
                continue
            else:
                LOG.warning('Not an Android Project: %s', dname)
                all_dirs['nonandroid'].append(dname)
        else:
            for path in subprojs:
                if is_android_project(path):
                    all_dirs['gradle'].append(path)
                else:
                    LOG.warning('Not an Android Project: %s', path)
                    all_dirs['nonandroid'].append(path)

    # all_dirs = sorted(all_dirs)
    all_dirs['gradle'] = sorted(all_dirs['gradle'], key=lambda x: (x.count('/'), x))
    all_dirs['nongradle'] = sorted(all_dirs['nongradle'], key=lambda x: (x.count('/'), x))
    return all_dirs


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
    if match:
        return match.groupdict()
    return None


def create_launch_command(package, activity, launcher=False):
    """
    Create command to launch activity from adb.

    Args:
        package: application package
        activity: name of activity to launch
        launcher: activity is a launcher activity

    Returns:
        command string

    """
    cmd = 'adb shell am start -n {0}/{1}'.format(package, activity)
    if launcher:
        cmd = ('adb shell monkey -p {0}'
               ' -c android.intent.category.LAUNCHER 1'.format(package))
    return cmd


def apkexists(rootdir, findall=False):
    """
    Check if apk already exists in directory.

    Args:
        rootdir: root directory to check
        findall: checks likely dirs for apk if True else only checks current dir

    Returns:
        None

    """
    if not findall:
        pattern = re.compile(r'.*(build/outputs/apk/debug|bin)$')
        dirs = find_directory_recursive(rootdir, pattern)  # '(build|bin)')
    else:
        dirs = [rootdir]

    # Slight speedup
    _findfast = find_file_pattern_fast

    files = []
    LOG.debug('Found %s dirs: %s', len(dirs), dirs)
    pattern = re.compile(r'(.+\.apk)$')
    for dname in tqdm(dirs, leave=False):
        files += _findfast(dname, pattern)

    LOG.debug('Found %s apks: %s', len(files), files)
    if not files:
        return None
    return [fname for fname in files
            if not fname.endswith('unaligned.apk') and os.path.isfile(fname)]


def parallel_apkexists(array, n_jobs=16, front_num=3):
    """
    Check if apk already exists in directory (runs in parallel).

    Args:
        rootdir: root directory to check
        findall: checks likely dirs for apk if True else only checks current dir

    Returns:
        None

    """
    if front_num > 0:
        front = [apkexists(a) for a in array[:front_num]]
    if n_jobs == 1:
        return front + [apkexists(a) for a in tqdm(array[front_num:])]
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        futures = [pool.submit(apkexists, a) for a in array[front_num:]]
        kwargs = {
            'total': len(futures), 'unit': 'it',
            'unit_scale': True, 'leave': True
        }
        # pylint: disable=unused-variable
        for fname in tqdm(as_completed(futures), **kwargs):
            pass

    out = []
    for i, future in tqdm(enumerate(futures)):
        # pylint: disable=broad-except
        try:
            out.append(future.result())
        except Exception as err:
            out.append(err)
    results = front + out
    results = [i for i in results if i]
    return [i for sublist in results for i in sublist]


def stop_gradle_daemons(rootdir):
    """
    Stop gradle daemons.

    Args:
        rootdir: current running directory

    Returns:
        None

    """
    LOG.debug('Stopping gradle daemons')
    cmd = '/home/yannes/Documents/development/gradle-4.4.1/bin/gradle --stop'
    task = mycommand.Command(cmd, cwd=rootdir, printout=False)
    log = task.run()
    LOG.debug('\n'.join(log))


def reset_directory(args, rootdir):
    """
    Stop gradle daemons.

    Args:
        args: dict of args
        rootdir: current running directory

    Returns:
        None

    """
    LOG.info('Resetting directory: %s', rootdir)
    cmd = 'git reset --hard HEAD'
    task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
    task.run()


def init_directory(args, rootdir, data, count=0):
    """
    Initialize project directory.

    Args:
        args: dict of args
        rootdir: current running directory
        data: dict of AndroidManifest data
        count: number of times this method has been run (defaults to 0)

    Returns:
        args

    """
    LOG.info('Initializing directory (count %d): %s, dirtype = %s',
             count, rootdir, args['dirtype'])
    sdk = os.environ['ANDROID_SDK']

    if args['dirtype'] in ['gradle', 'ant', 'maven', 'android']:
        with open(rootdir + '/local.properties', 'w') as wfh:
            wfh.write('sdk.dir=' + sdk + '\n')
            if 'ANDROID_NDK' in os.environ:
                wfh.write('ndk.dir=' + os.environ['ANDROID_NDK'] + '\n')

        cmd = 'gradle wrapper --gradle-version=4.4.1'
        LOG.info('Initializing: %s', cmd)
        task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
        log = task.run(error_pattern=ANT_ERROR_PATTERN, timeout=TASK_TIMEOUT)
        if os.path.exists('{}/build.gradle'.format(rootdir)):
            gradle_helper.fix_gradle('{}/build.gradle'.format(rootdir))

        os.chmod('{0}/gradlew'.format(rootdir), 0755)
        LOG.debug('Setup gradle: %s', log)
        files = find_files_recursive(rootdir, 'gradle-wrapper.properties')
        for fname in files:
            gradle_helper.replace_gradle_url(fname)

        files = find_files_recursive(rootdir, 'build.gradle')
        for fname in files:
            gradle_helper.replace_build_version(fname)
            gradle_helper.replace_gradle_classpath(fname)
        if not log and count < 2:
            LOG.debug('Error initializing:\n%s', task.get_log())
            init_directory(args, rootdir, data, count=count + 1)
        elif not log and count >= 2:
            LOG.info('Error initializing:\n%s', '\n'.join(task.get_log()))
    elif args['dirtype'] in ['ant', 'maven', 'android']:
        activity = data['activity'].split('/')[-1].split('.')[-1].replace('-', '')
        if not activity.strip():
            activity = 'MainActivity'
        appname = data['appname'].replace('-', '')
        if '.' in appname:
            appname = appname.split('.')[-1]
        LOG.info('%s: Converting %s directory to gradle',
                 appname, args['dirtype'])

        androidcmd = 'android'
        cmd = ('{} create project --gradle --gradle-version 0.11.+ --path . '
               '--activity {} -t 2 -n {} -k {}'
               .format(androidcmd, activity, appname, data['package']))
        LOG.info('Initializing: %s', cmd)
        task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
        log = task.run()
        if os.path.exists('{}/build.gradle'.format(rootdir)):
            gradle_helper.fix_gradle('{}/build.gradle'.format(rootdir))
        args['dirtype'] = 'gradle'
        LOG.debug('Log: %s', log)
    return args


def build(args, rootdir):
    """
    Build project.

    Args:
        args: dict of args
        rootdir: current running directory

    Returns:
        True if build completes, else False

    """
    LOG.info('Building directory: %s', rootdir)
    if args['dirtype'] == 'gradle':
        cmd = 'gradle --project-cache-dir ~/Desktop/gradle-cache assembleDebug'
        err_pattern = [DEFAULT_ERROR_PATTERN, ANT_ERROR_PATTERN]
    elif args['dirtype'] == 'ant':
        cmd = 'ant debug'
        err_pattern = ANT_ERROR_PATTERN
    elif args['dirtype'] == 'maven':
        cmd = 'mvn build -DskipTests'
        err_pattern = ANT_ERROR_PATTERN
    LOG.info('Building: ' + cmd)
    task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
    log = task.run(error_pattern=err_pattern, timeout=TASK_TIMEOUT)
    # return False if not log else True
    if not log:
        LOG.error('Failed:\n%s', '\n'.join(task.get_log()))
        return False
    files = find_file_pattern_recursive(rootdir, '.apk')
    if not files:
        return False
    return True


def install(args, rootdir):
    """
    Install project.

    Args:
        args: dict of args
        rootdir: current running directory

    Returns:
        None

    """
    apkpaths = apkexists(rootdir)
    if apkpaths:
        LOG.info('Installing %s from adb', apkpaths)
        cmd = 'adb install -r {}'.format(apkpaths[0])
    elif args['dirtype'] == 'gradle':
        cmd = './gradlew --project-cache-dir ~/Desktop/gradle-cache installDebug'
    elif args['dirtype'] == 'ant':
        cmd = 'ant install'
    elif args['dirtype'] == 'maven':
        cmd = 'mvn install -DskipTests'
    LOG.info('Installing: %s', cmd)
    task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
    log = task.run()
    LOG.debug('Log: %s', log)


def test(args, rootdir):
    """
    Test project.

    Args:
        args: dict of args
        rootdir: current running directory

    Returns:
        True if build completes, else False

    """
    cmd = './gradlew --project-cache-dir ~/Desktop/gradle-cache cAT'
    LOG.info('Testing: %s', cmd)
    task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
    log = task.run()
    LOG.debug('Log: %s', log)


def launch(args, data):
    """
    Launch project.

    Args:
        args: dict of args
        data: dict of AndroidManifest data

    Returns:
        None

    """
    cmd = create_launch_command(data.get('package'), data.get('activity'),
                                data.get('launcher'))
    LOG.info('Launching: %s', cmd)
    task = mycommand.Command(cmd, printout=args['verbose'])
    log = task.run()
    LOG.debug('Log: %s', log)


def clean(args, rootdir):
    """
    Clean project.

    Args:
        args: dict of args
        rootdir: current running directory

    Returns:
        None

    """
    if args['dirtype'] == 'gradle':
        cmd = './gradlew --project-cache-dir ~/Desktop/gradle-cache clean'
    elif args['dirtype'] == 'ant':
        cmd = 'ant clean'
    elif args['dirtype'] == 'maven':
        cmd = 'mvn clean'
    LOG.info('Cleaning: %s', cmd)
    task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
    log = task.run()
    LOG.debug('Log: %s', log)


def uninstall(args, rootdir):
    """
    Uninstall project.

    Args:
        args: dict of args
        rootdir: current running directory
        data: dict of AndroidManifest data

    Returns:
        None

    """
    if args['dirtype'] == 'gradle':
        cmd = './gradlew --project-cache-dir ~/Desktop/gradle-cache uninstallAll'
    elif args['dirtype'] == 'ant':
        cmd = 'ant uninstall'
    elif args['dirtype'] == 'maven':
        cmd = 'mvn uninstall'
    LOG.info('Uninstalling: %s', cmd)

    task = mycommand.Command(cmd, cwd=rootdir, printout=args['verbose'])
    log = task.run()
    LOG.debug('Log: %s', log)


def copyapk(args, rootdir, data):
    """
    Copy apk from directory to outdir in args.

    Args:
        args: dict of args
        rootdir: current running directory
        data: dict of AndroidManifest data

    Returns:
        True if copy completes, else False

    """
    files = find_file_pattern_recursive(rootdir, '.apk')
    if not files:
        return False
    newname = '{0}/{1}.apk'.format(args['outdir'], data['appname'])

    if len(files) > 1:
        LOG.info('Found multiple apk files: %s', files)
    LOG.info('Copying %s to %s', files[0], newname)
    if args['dryrun']:
        return True
    shutil.copyfile(files[0], newname)
    return True
