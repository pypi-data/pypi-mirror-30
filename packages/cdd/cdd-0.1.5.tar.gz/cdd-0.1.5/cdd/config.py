from __future__ import print_function
from __future__ import unicode_literals

import codecs
import sys
import os
import json
import datetime

def to_unicode(obj, encoding='utf-8'):
    assert isinstance(obj, basestring), type(obj)
    if isinstance(obj, unicode):
        return obj

    for encoding in ['utf-8', 'latin1']:
        try:
            obj = unicode(obj, encoding)
            return obj
        except UnicodeDecodeError:
            pass

    assert False, "tst: non-recognized encoding"


class NoConfigFileName(Exception): pass
class CorruptedFile(Exception): pass

class Config(object):

    __instance = None
    FLAGS = ['debug']
    filename = None

    def __new__(cls, filename=None, init=None):
        Config.filename = Config.filename or filename
        if not Config.filename:
            raise NoConfigFileName()

        if Config.__instance is not None:
            return Config.__instance

        Config.__instance = object.__new__(cls)
        self = Config.__instance
        if init:
            self.data = init


        # initialization
        self.data = None
        return self


    def __setitem__(self, key, value):
        if self.data is None:
            self.load()

        if key in Config.FLAGS:
            value = boolean(value)
        
        self.data[key] = value


    def __getitem__(self, key):
        if self.data is None:
            self.load()

        return self.data[key]


    def __contains__(self, key):
        if self.data is None:
            self.load()

        return key in self.data


    def pop(self, key):
        if self.data is None:
            self.load()

        self.data.pop(key, None)


    def load(self, exit_on_fail=False):
        if not os.path.exists(Config.filename):
            return

        # actually read from file system
        try:
            with codecs.open(Config.filename, mode='r', encoding='utf-8') as f:
                self.data = json.loads(to_unicode(f.read()))

        except ValueError:
            msg = "cdd: %s is corrupted" % Config.filename
            if exit_on_fail:
                print(msg, file=sys.stderr)
                sys.exit()

            raise CorruptedFile(msg)


    def save(self):
        if self.data is None:
            self.load()

        with codecs.open(Config.filename, mode="w", encoding='utf-8') as f:
            f.write(json.dumps(
                self.data,
                indent=2,
                separators=(',', ': ')
            ))


    def get(self, key, default=None):
        if self.data is None:
            self.load()

        return self.data.get(key, default)
