#!/usr/bin/env python
import os
# me
from fullpath import fullpath
from public import public


def mkdir(path):
    if path.find("/") > 0 and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))


def utime(path):
    try:
        os.utime(path, None)
    except Exception:
        open(path, 'a').close()


@public
def touch(path):
    if not path:
        return
    path = fullpath(path)
    mkdir(path)
    utime(path)
