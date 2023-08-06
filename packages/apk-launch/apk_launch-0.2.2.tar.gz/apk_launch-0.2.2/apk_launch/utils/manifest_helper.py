"""
manifest_helper is a helper class for the AndroidManifest.

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

import logging
import json
import xmltodict

from apk_launch.utils import apk_utils

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
LOG = logging.getLogger(__name__)


def get_name(item):
    """
    Get name of component from item.

    Args:
        item: xml component object

    Returns:
        String of component name

    """
    name = item.get('@android:name')
    if not name:
        name = item.get('@a:name')

    return name


def is_launcher_action(action, category):
    """
    Check if action xml object is defined as a launcher activity.

    Args:
        item: xml component object

    Returns:
        True if launcher activity, else False

    """
    actnames = ([get_name(action)] if isinstance(action, dict)
                else [get_name(act) for act in action])

    cats = ([get_name(category)] if isinstance(category, dict)
            else [get_name(cat) for cat in category])

    LOG.debug('Actions: %s', actnames)
    LOG.debug('Categories: %s', cats)

    for actname in actnames:
        for cat in cats:
            if actname == 'android.intent.action.MAIN' \
                    and cat == 'android.intent.category.LAUNCHER':
                return True

    return False


def check_launcher_activity(activity):
    """
    Parse xml activity for name of launcher activity.

    Args:
        activity: xml object from AndroidManifest

    Returns:
        None if not found, else name of launcher activity

    """
    if isinstance(activity.get('intent-filter'), dict):
        filters = [activity.get('intent-filter')]
    else:
        filters = activity.get('intent-filter')
    if not filters:
        return None

    for intentfilter in filters:
        name = get_name(activity)
        if isinstance(intentfilter, dict):
            actions = [intentfilter.get('action')]
        else:
            actions = intentfilter.get('action')
        category = intentfilter.get('category')
        for action in actions:
            if not action or not category:
                return None

            if is_launcher_action(action, category):
                return name
    return None


def parse_manifest_activity(data, act, search_activity=None):
    """
    Parse AndroidManifest Activity for information.

    Args:
        data: current dict of android manifest
        act: activity dict
        search_activity: specific activity to look for (defaults to None)

    Returns:
        dict of AndroidManifest data

    """
    for key in act.keys():
        if key.split(':')[-1] == 'name':
            name = get_name(act)
            break
    LOG.debug('Checking act %s: "%s"', search_activity, name)

    if search_activity:
        if search_activity == name:
            data['activity'] = name
    else:
        launchname = check_launcher_activity(act)
        if launchname:
            data['activity'] = launchname
            data['launcher'] = True
    if not data['activity']:
        data['activity'] = name
    return data


def parse_manifest(filename, search_activity=None):
    """
    Parse AndroidManifest for information.

    Args:
        filename: path of AndroidManifest.xml
        search_activity: provide specific activty to parse (defaults to None)

    Returns:
        dict of AndroidManifest data

    """
    LOG.debug('Parsing Manifest file: %s', filename)
    data = {
        'package': '',
        'activity': '',
        'launcher': False,
    }
    try:
        with open(filename, 'r') as rfh:
            text = '\n'.join(rfh.readlines())
    except TypeError as err:
        LOG.error('Error on file "%s": %s', filename, err)
        return None

    try:
        # pylint: disable=eval-used
        xmldict = eval(json.dumps(xmltodict.parse(text)))
    except NameError as err:
        LOG.error('Error with manifest file %s: %s', filename, err)
        return None

    manifest = xmldict.get('manifest')

    data['package'] = manifest.get('@package')
    app = manifest.get('application')
    if not app:
        LOG.error('Error: cannot find application in manifest file %s',
                  filename)
        return data

    acts = ([app.get('activity')] if isinstance(app.get('activity'), dict)
            else app.get('activity'))
    if not acts:
        LOG.error('Error: cannot find launch activity in manifest file %s',
                  filename)
        return data
    data['launcher'] = False

    for act in acts:
        data = parse_manifest_activity(data, act, search_activity)
    return data


def setup_manifest_data(rootdir, filename, search_activity=None, appname=None, force=False):
    """
    Set up dictionary of AndroidManifest information.

    Args:
        rootdir: root directory of application
        filename: path of AndroidManifest.xml
        search_activity: provide specific activty to parse (defaults to None)

    Returns:
        dict of AndroidManifest data

    Raises:
        ValueError if parse_manifest returns None

    """
    data = parse_manifest(filename, search_activity=search_activity)
    LOG.debug('Data: %s', data)
    if not data:
        LOG.warning('parse_manifest returned null for %s', rootdir)
        raise ValueError

    if not appname:
        # rootdir = args['rootdir']
        tmpname = rootdir[:-1] if rootdir.endswith('/') else rootdir
        appname = tmpname.split('/')[-1]

    apkpaths = apk_utils.apkexists(rootdir)
    if apkpaths and not force:
        LOG.debug('Apk already exists: %s', apkpaths)
        # newname = '{}/{}.apk'.format(args['outdir'], data['appname'])
        LOG.info('Apk %s already exists. Skipping...', data['appname'])
        data['paths'] = apkpaths
        return data

    try:
        if data and 'activity' in data and '/' not in data.get('activity', ''):
            activity = data.get('activity', '')
            if not activity.startswith('.'):
                activity = '.' + activity
            data['activity'] = '{0}/{1}'.format(data.get('package'), activity)
    # pylint: disable=broad-except
    except Exception:
        LOG.error('Data: %s', data)

    return data
