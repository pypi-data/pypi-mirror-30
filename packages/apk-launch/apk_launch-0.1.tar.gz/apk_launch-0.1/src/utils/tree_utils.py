"""
tree_utils is a helper file for handling trees.

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
import gzip
import errno
import json
import logging
import treelib
from treelib import Tree
from tqdm import tqdm

logging.basicConfig(format='%(message)s', level=logging.INFO)
LOG = logging.getLogger(__name__)


def convert_packages_to_trees(listdata):
    """
    Convert list of packages to trees.

    Args:
        listdata: list of packages

    Returns:
        list of trees

    """
    trees = {}
    for i, data in tqdm(enumerate(listdata), leave=False, total=len(listdata)):
        LOG.debug('Package[%s]: %s', i, data)
        title = data['name'].strip()
        parts = title.split('.')
        child = parts[-1].strip()
        if child == '<TOTAL>':
            continue

        if len(parts) < 2:
            parent = None
        else:
            parent = '.'.join(parts[:-1])

        root = parts[0]
        if root not in trees or not parent:
            trees[child] = Tree()
            trees[child].create_node(child, child, data=data)
            LOG.debug('Created new package tree with root: %s', root)
            # trees[child].show()
        else:
            trees[root].create_node(title, title, parent=parent, data=data)
            # trees[root].show()

    for key in trees:
        LOG.debug('Package Tree %s', key)
    return trees


def add_node_to_tree(tree, child, parent, data):
    """
    Add node to tree.

    Args:
        tree: current tree
        child: child to add
        parent: parent to add child to
        data: child data

    Returns:
        list of trees

    """
    if child in tree:
        return tree
    if not parent and child is not None:
        tree.create_node(child, child, data=data)
        return tree
    elif not parent:
        return Tree

    newparent = '.'.join(parent.split('.')[:-1])

    tree = add_node_to_tree(tree, parent, newparent, None)
    tree.create_node(child, child, parent=parent, data=data)
    return tree


def convert_classes_to_trees(classdata):
    """
    Convert list of classes to trees.

    Args:
        classdata: list of classes

    Returns:
        list of trees

    """
    trees = {}
    for i, data in tqdm(enumerate(classdata), leave=False, total=len(classdata)):
        LOG.debug('Classes[%s]: %s', i, data)
        title = data['name'].strip()
        parts = title.split('.')
        child = parts[-1].strip()
        if child == '<TOTAL>':
            continue

        if len(parts) < 2:
            parent = None
        else:
            parent = '.'.join(parts[:-1])

        root = parts[0]

        if root not in trees:
            trees[root] = Tree()
            trees[root].create_node(root, root, data=data)
            LOG.debug('Created new class tree with root: %s', root)
        add_node_to_tree(trees[root], child, parent, data)
    return trees


def convert_fields_to_trees(fielddata):
    """
    Convert list of fields to trees.

    Args:
        fielddata: list of fields

    Returns:
        list of trees

    """
    trees = {}
    for i, data in tqdm(enumerate(fielddata), leave=False, total=len(fielddata)):
        LOG.debug('Fields[%s]: %s', i, data)
        title = data['name'].strip()
        parts = title.split('.')
        child = parts[-1].strip()
        if child == '<TOTAL>':
            continue

        if len(parts) < 2:
            parent = None
        else:
            parent = '.'.join(parts[:-1])

        root = parts[0]

        if root not in trees:
            trees[root] = Tree()
            trees[root].create_node(root, root, data=data)
            LOG.debug('Created new field tree with root: %s', root)
            # trees[child].show()
        add_node_to_tree(trees[root], child, parent, data)
        field = data['data_type'] + ' ' + data['field']
        add_node_to_tree(trees[root], field, title, data)

    for key in trees:
        LOG.debug('Field Tree %s', key)
    return trees


def convert_methods_to_trees(methoddata):
    """
    Convert list of methods to trees.

    Args:
        methoddata: list of methods

    Returns:
        list of trees

    """
    trees = {}
    for i, data in tqdm(enumerate(methoddata), leave=False, total=len(methoddata)):
        LOG.debug('Methods[%s]: %s', i, data)
        title = data['name'].strip()
        parts = title.split('.')
        child = parts[-1].strip()
        if child == '<TOTAL>':
            continue

        if len(parts) < 2:
            parent = None
        else:
            parent = '.'.join(parts[:-1])

        root = parts[0]

        if root not in trees:
            trees[root] = Tree()
            trees[root].create_node(root, root, data=data)
            LOG.debug('Created new method tree with root: %s', root)
            # trees[child].show()
        add_node_to_tree(trees[root], child, parent, data)
        method = data['methodname']
        add_node_to_tree(trees[root], method, title, data)

    for key in trees:
        LOG.debug('Tree %s', key)
    return trees


def organize_as_trees(classes, fields, methods, packages):
    """
    Convert lists of classes, fields, methods, packages to trees.

    Args:
        classes: list of classes
        fields: list of fields
        methods: list of methods
        packages: list of packages

    Returns:
        class_trees: list of class trees
        field_trees: list of field trees
        method_trees: list of method trees
        package_trees: list of package trees

    """
    LOG.debug('%s methods', len(methods))
    LOG.debug('%s packages', len(packages))
    LOG.debug('%s classes', len(classes))
    LOG.debug('%s fields', len(fields))

    package_trees = convert_packages_to_trees(packages)
    class_trees = convert_classes_to_trees(classes)
    field_trees = convert_fields_to_trees(fields)
    method_trees = convert_methods_to_trees(methods)

    return class_trees, field_trees, method_trees, package_trees


def print_trees(class_trees, field_trees, method_trees, package_trees):
    """
    Print trees of classes, fields, methods, packages.

    Args:
        classes: list of classes
        fields: list of fields
        methods: list of methods
        packages: list of packages

    Returns:
        None

    """
    for tree_key in package_trees:
        LOG.info('Package tree %s', tree_key)
        package_trees[tree_key].show()

    for tree_key in class_trees:
        LOG.info('Class tree %s', tree_key)
        class_trees[tree_key].show()

    for tree_key in field_trees:
        LOG.info('Field tree %s', tree_key)
        field_trees[tree_key].show()

    for tree_key in method_trees:
        LOG.info('Method tree %s', tree_key)
        method_trees[tree_key].show()


def get_tree_filename(inputfile, outdir, typename, tree_key):
    """
    Convert to filename for tree.

    Args:
        inputfile: input filename
        outdir: output directory
        typename: category type
        tree_key: tree key

    Returns:
        filename

    """
    baseapk = inputfile.split('/')[-1]
    path = '{0}/{1}'.format(outdir, '.'.join(baseapk.split('.')[:-1]))
    filename = '{0}/{1}_{2}.dat'.format(path, typename, tree_key)
    return filename


def save_tree(args, tree, typename, tree_key):
    """
    Save tree to file.

    Args:
        args: command line args
        tree: tree to store
        typename: tree type
        tree_key: tree key

    Returns:
        None

    """
    baseapk = args['input'].split('/')[-1]
    path = '{0}/{1}'.format(args['outdir'], '.'.join(baseapk.split('.')[:-1]))
    filename = '{0}/{1}_{2}.tree.gz'.format(path, typename, tree_key)
    LOG.debug('Saving %s %s to %s', args['input'], typename, filename)

    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    data = tree.to_json(with_data=True)
    if os.path.exists(filename) and not args['force']:
        LOG.debug('File %s already exists. Skipping...', filename)
    with gzip.open(filename, 'wb') as wfh:
        wfh.write(data)


def save_all_trees(args, data):
    """
    Save all trees to file.

    Args:
        args: command line args
        data: all tree data

    Returns:
        None

    """
    for tree_type in data:
        for tree_key in data[tree_type]:
            save_tree(args, data[tree_type][tree_key], tree_type, tree_key)


def data_to_tree(data, parent=None, tree=Tree()):
    """
    Convert data to tree.

    Args:
        data: apk data
        parent: parent to store tree to (defaults to None)
        tree: tree to store to (defaults to new Tree)

    Returns:
        tree (as treelib.Tree)

    """
    LOG.debug('\ndata_to_tree:')
    if isinstance(data, dict):
        key = data.keys()[0]
        LOG.debug('Adding %s (data %s) to tree', key, data.get(key).get('data'))
        try:
            tree.create_node(key, key, parent=parent, data=data.get(key).get('data'))
        # pylint: disable=no-member
        except treelib.exceptions.MultipleRootError as err:
            LOG.error('Error: %s - root %s, parent %s', err, key, parent)
            LOG.error('Old tree: ')
            tree.show()
            sys.exit(1)

        LOG.debug('Remaining: %s', data[key])
        if 'children' in data[key]:
            LOG.debug('Iterating children: %s', data[key])
            children = data[key]['children']
            for child in children:
                tree = data_to_tree(child, parent=key, tree=tree)
        else:
            return tree
    elif isinstance(data, list):
        LOG.error('Error: data_to_tree list %s', data)
        sys.exit(1)
    else:
        LOG.debug('Adding node (%s): %s', type(data), data)
        tree.create_node(data, data, parent=parent, data=data.get('data'))
    LOG.debug('Current Tree:\n%s\n', tree)
    return tree


def read_treefile(treefile):
    """
    Read tree from file.

    Args:
        treefile: file containing tree

    Returns:
        tree (as treelib.Tree)

    """
    LOG.debug('read_treefile: %s', treefile)
    if treefile.endswith('.gz'):
        with gzip.open(treefile, 'rb') as rfh:
            data = json.load(rfh)
    else:
        with open(treefile, 'r') as rfh:
            data = json.load(rfh)
    LOG.debug(data)
    tree = data_to_tree(data, tree=Tree())
    LOG.debug('read_treefile: complete %s', tree)
    # tree.show()
    return tree


def union_trees(tree1, tree2):
    """
    Combine two trees.

    Args:
        tree1: tree (as treelib.Tree)
        tree2: tree (as treelib.Tree)

    Returns:
        matches: paths in both trees
        remaining: paths in only one tree

    """
    LOG.info('Comparing trees...')
    LOG.info('Tree 1: %s', tree1)
    LOG.info('Tree 2: %s', tree2)

    paths1 = set(['.'.join(path[-2:]) for path in tree1.paths_to_leaves()])
    LOG.info('Tree 1 paths: %s', paths1)

    paths2 = set(['.'.join(path[-2:]) for path in tree2.paths_to_leaves()])
    LOG.info('Tree 2 paths: %s', paths2)

    matches = paths1 & paths2
    remaining = paths1 - matches
    LOG.info('Matches: %s', matches)
    LOG.info('Remaining: %s', remaining)
    return matches, remaining
