#!/usr/bin/env python2
from __future__ import print_function

__all__ = ['show']

def show(*targets):
    _targets = [ ]
    for target in targets:
        _targets.append(type(target)) 
        _targets.append(target)
    print(*_targets)

if __name__ == "__main__":
    pass
