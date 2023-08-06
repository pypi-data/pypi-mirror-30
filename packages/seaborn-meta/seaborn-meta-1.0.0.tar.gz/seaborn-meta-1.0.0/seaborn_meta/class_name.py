""" This module contains some functionality that would be helpful for
    meta programming
"""
import glob
import os


def class_name_to_instant_name(name):
    """ This will convert from 'ParentName_ChildName' to
    'parent_name.child_name' """
    name = name.replace('/', '_')
    ret = name[0].lower()
    for i in range(1, len(name)):
        if name[i] == '_':
            ret += '.'
        elif '9' < name[i] < 'a' and name[i - 1] != '_':
            ret += '_' + name[i].lower()
        else:
            ret += name[i].lower()
    return ret


def instant_name_to_class_name(name):
    """
        This will convert from 'parent_name.child_name' to
        'ParentName_ChildName'
    :param name: str of the name to convert
    :return: str of the converted name
    """
    name2 = ''.join([e.title() for e in name.split('_')])
    return '_'.join([e[0].upper() + e[1:] for e in name2.split('.')])


def url_name_to_class_name(name):
    """
        This will convert a class name to the url path name
    :param name: str of the name to convert
    :return: str of the converted name
    """
    name = name.replace('/', '.')
    return instant_name_to_class_name(name)


def create_init_files(path):
    """
        This will create __init__.py for a module path and every subdirectory
    :param path: str of the path to start adding __init__.py to
    :return: None
    """
    python_files = sorted([os.path.basename(file_)[:-3] for file_ in
                           glob.glob(os.path.join(path, '*.py'))
                           if not file_.endswith('__init__.py')])

    folders = sorted([os.path.basename(folder) for folder in os.listdir(path)
                      if os.path.isdir(os.path.join(path, folder))])
    with open(path + '/__init__.py', 'w') as fn:
        if python_files:
            [fn.write('from %s import *\n' % file_) for file_ in python_files]
            [fn.write('import %s\n' % folder) for folder in folders]
    for folder in folders:
        create_init_files(os.path.join(path, folder))
