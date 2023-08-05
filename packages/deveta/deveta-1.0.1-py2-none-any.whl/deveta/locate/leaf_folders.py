#!/usr/bin/env python2
''' leaf_folders docstring '''
from __future__ import print_function
from collections import defaultdict
import argparse
import os
import sys

__all__ = ['leaf_folders']


class RadixTrie(object):
    ''' RadixTrie, used to store directory tree information
        note: target is used to indicate a node's associated key and 
              absolute/relative paths
    '''
    def __init__(self,  seperator='/', descendents=None):
        self.seperator = seperator
        self.node = defaultdict(RadixTrie)
        if isinstance(descendents, list):
            for desc in descendents:
                self.insert(desc)

    def __contains__(self, target):
        ''' checks if target is in RadixTrie
        '''
        radixtrie = self
        for directory in target.split(self.seperator):
            if directory in radixtrie.node:
                radixtrie = radixtrie.node[directory]
            else:
                return False
        return True

    def insert(self, target):
        ''' inserts target into trie
        '''
        radixtrie = self
        for i, directory in enumerate(target.split(self.seperator)):
            if directory == '':
               directory = self.seperator
            radixtrie = radixtrie.node[directory]

    def is_leaf(self, target=None):
        ''' checks if target is a leaf node
        '''
        radixtrie = self
        if isinstance(target, type(None)):
            return len(radixtrie.node.values()) == 0
        for directory in target.split(self.seperator):
            if directory in radixtrie.node:
                radixtrie = radixtrie.node[directory]
            else:
                return False
        return radixtrie.is_leaf()

    def __str__(self):
        ''' computes nicely printable string object'''
        output_chunks = self.to_list(leafs_only=False)
        return '\n'.join(output_chunks)

    def to_list(self, leafs_only=False, pwd=''):
        ''' Returns RadixTrie as a list object '''
        def descendent(pwd):
            return pwd != ''
        output_chunks = []
        for key in self.node:
            if key == self.seperator:
                output_chunks.extend(self.node[key].to_list(leafs_only=leafs_only))
                continue
            path = pwd+self.seperator+key if descendent else key
            if not leafs_only or (leafs_only and self.node[key].is_leaf()):
                output_chunks.append(path)
            output_chunks.extend(self.node[key].to_list(leafs_only=leafs_only, pwd=path))
        return output_chunks
        

class Error(Exception):
     pass

class PathNotFoundError(Error):
     def __init__(self, value):
         self.msg = "The provided path '{}' does not exist. Please provide a valid path.".format(value)
     def __str__(self):
         return self.msg

class PathTypeError(Error):
     def __init__(self, value):
         self.msg = "The provided path '{}' is a file. Please provide a valid directory.".format(value)
     def __str__(self):
         return self.msg

class InvalidArgumentError(Error):
     def __init__(self, value):
         self.msg = "Invalid Argument: {}".format(value)
     def __str__(self):
         return self.msg

def path_exists(path):
    try:
        assert os.path.exists(path)
    except AssertionError as e:
        raise PathNotFoundError(path)

def is_valid_directory(path):
    try:
        assert not os.path.isfile(path)
    except AssertionError as e:
        raise PathTypeError(path)

def validate_arguments(path):
    try:
        path_exists(path)
        is_valid_directory(path)
    except (PathNotFoundError, PathTypeError) as e:
        raise InvalidArgumentError(e)

def generate_directory_list(path):
    ''' Creates list of all directories by walking path '''
    return map(lambda x : x , sorted([x[0] for x in os.walk(path) if os.path.isdir(x[0])]))[1:]

def leaf_folders(path='.'):
    ''' Description: 
          finds all of the leaf directorys using a trie data structure to store the walk
        Arguments:
          path, the location to search for leaf nodes
        Returns:
          list object containing leaf fodlers within path 
    '''
    try:
        leafs = []
        absolute_path = os.path.abspath(path)
        validate_arguments(absolute_path)
        directories = generate_directory_list(absolute_path)
        radixtrie = RadixTrie(descendents=directories)
        leafs = radixtrie.to_list(leafs_only=True)
    except InvalidArgumentError as e:
        print(e, '\n', file=sys.stderr)
    finally:
        return leafs


def get_args():
    parser = argparse.ArgumentParser(description='Find all leaf folders given a target path.')
    parser.add_argument('target_paths', metavar='PATHS', type=str, nargs='+',
                    help='paths to search for leaf subfolders, or if it is one itself')
    return parser.parse_args()

def main():
    ''' main
    '''
    args = get_args()
    leafs = []
    for target_path in args.target_paths:
        _result = leaf_folders(path=target_path)
        leafs.extend(_result)
    leafs = set(leafs)
    print(*leafs, sep='\n')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        os._exit()

