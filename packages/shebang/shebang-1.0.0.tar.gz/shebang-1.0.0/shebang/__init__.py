#!/usr/bin/env python
# -*- coding: utf-8 -*-s
import os
from isbinaryfile import isbinaryfile
from read import read
from public import public


@public
def is_shebang(l):
    """return True if line is shebang"""
    return l and l.find("#!") == 0


def read_shebang(path):
    content = read(path)
    lines = content.splitlines()
    if not lines:
        return
    if lines[0].find("#!") == 0:
        return lines[0].replace("#!", "", 1).strip()


@public
def shebang(path):
    """return file/string shebang"""
    if not path:
        return
    path = str(path)
    if not os.path.exists(path) or isbinaryfile(path):
        return
    return read_shebang(path)
