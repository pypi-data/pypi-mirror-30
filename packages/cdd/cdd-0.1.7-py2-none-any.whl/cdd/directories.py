from __future__ import print_function
from __future__ import unicode_literals

import os

class Directories:
    def __init__(self, directories):
        self.data = directories

    def __contains__(self, d):
        dirs = self.data
        index = next((i for i in xrange(len(dirs)) if dirs[i][0] == d), len(dirs))
        return index < len(dirs)
        

    def add(self, d):
        dirs = self.data
        index = next((i for i in xrange(len(dirs)) if dirs[i][0] == d), len(dirs))
        if index == len(dirs):
            dirs.append([d, 0])

    def remove(self, d):
        dirs = self.data
        index = next((i for i in xrange(len(dirs)) if dirs[i][0] == d), len(dirs))
        if index < len(dirs):
            dirs.pop(index)

    def hit(self, d):
        dirs = self.data
        index = next((i for i in xrange(len(dirs)) if dirs[i][0] == d), len(dirs))
        if index < len(dirs):
            dirs[index][1] += 1
            dirs.sort(key=lambda e: e[1], reverse=True)
        

def is_match(pattern, directory):
    return pattern.lower() in directory.lower()


def matching_from(pattern, directories, from_dir):
    alternatives = [d[0] for d in directories if is_match(pattern, os.path.basename(d[0]))]
    if not alternatives:
        return [None, []]

    if from_dir not in alternatives:
        select = alternatives[0]

    else: # from_dir in alternatives:
        index = alternatives.index(from_dir)
        alternatives[index]
        select = alternatives[(index + 1) % len(alternatives)]

    return [select, alternatives]
