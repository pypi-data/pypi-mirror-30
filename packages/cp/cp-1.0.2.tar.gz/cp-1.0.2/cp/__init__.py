#!/usr/bin/env python
from distutils import dir_util
import os
import shutil
# me
from assert_exists import assert_exists
from public import public


def cp_file(source, target):
    if (os.path.exists(target) or os.path.lexists(target)):
        if os.path.isfile(source) != os.path.isfile(target):
            os.unlink(target)
    shutil.copy(source, target)


def cp_dir(source, target):
    if not os.path.exists(target):
        os.makedirs(target)
    dir_util.copy_tree(source, target)


def get_target(source, target):
    if os.path.isfile(source) and os.path.isdir(target):
        return os.path.join(target, os.path.basename(source))
    return target


def copy(source, target):
    target = get_target(source, target)
    if os.path.isfile(source) or os.path.islink(source):
        cp_file(source, target)
    if os.path.isdir(source):
        cp_dir(source, target)


@public
def cp(source, target, force=True):
    if (os.path.exists(target) and not force) or source == target:
        return
    assert_exists(source)
    copy(source, target)
