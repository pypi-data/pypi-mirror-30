#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
# me
from fullpath import fullpath
from isstring import isstring
from public import public


def mkdir(path):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

# TypeError: str() takes at most 1 argument (2 given)


def convert_bytes(content):
    try:
        return str(content, "utf-8")  # python3
    except TypeError:
        return str(content)  # python2


def convert(content):
    if content is None:
        return ""
    if isinstance(content, dict):
        return json.dumps(content)
    if str(content.__class__) == "<class 'bytes'>":
        return convert_bytes(content)
    return str(content)


@public
def write(path, content):
    """write to file and return fullpath"""
    path = fullpath(path)
    content = convert(content)
    mkdir(path)
    try:
        unicode()
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        open(path, "w").write(content)
    except NameError:
        # NameError: name 'unicode' is not defined
        open(path, "w", encoding="utf-8").write(content)
