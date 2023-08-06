#!/usr/bin/env python
import os
import shutil
# me
from fullpath import fullpath
from public import public

# os.unlink and shutil.rmtree replacement


def rm_file(path):
    if os.path.isfile(path) or os.path.islink(path):
        os.unlink(path)


def rm_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


@public
def rm(path):
    if not path or not os.path.exists(path):
        return
    path = fullpath(path)
    rm_file(path)
    rm_dir(path)
