#!/usr/bin/env python2
''' module docstring'''
from __future__ import print_function
from os.path import dirname, abspath, isdir, isfile
from os import walk
from inspect import stack

__all__ = ['this_file', 'this_dir', 'parent_dir', 'directories', 'files']

def this_file():
    called_from = stack()[1][1]
    path = abspath(called_from)
    return path

def this_dir():
    called_from = stack()[1][1]
    _dir = dirname(abspath(called_from))
    return _dir

def parent_dir():
    called_from = stack()[1][1]
    _dir = dirname(dirname(abspath(called_from)))
    return _dir

def directories(path):
    return map(lambda x : x , sorted([x[0] for x in walk(path) if isdir(x[0])]))[1:]

def files(path):
    path = path if path[-1] != '/' else path[:-1]
    return map(lambda x : x , sorted(['/'.join([x[0],y]) for x in walk(path) for y in list(x)[2] ]))

if __name__ == "__main__":
    print(files('/home/archie/repo/personal-website/personalwebsite/'))
