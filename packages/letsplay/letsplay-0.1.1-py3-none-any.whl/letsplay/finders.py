import glob
import os

from .song import Song


class BaseFinder(object):
    def search(self, phrase):
        ''' Returns iterable of Songs matching search phrase'''
        raise NotImplementedError


class GlobFinder(object):
    def search(self, phrase):
        path = os.path.realpath(os.path.expanduser(phrase))

        return map(Song.local, filter(
            os.path.isfile, glob.iglob('%s*' % path, recursive=True)))


class FinderAlreadyRegistered(Exception):
    pass


class FindersRegistry(object):
    def __init__(self):
        self._finders = {}

    def register(self, scheme, finder):
        scheme = scheme.lower()
        if scheme in self._finders:
            raise FinderAlreadyRegistered(scheme)
        self._finders[scheme] = finder

    def get(self, scheme):
        return self._finders[scheme]


registry = FindersRegistry()
registry.register('glob', GlobFinder())


def find(uri):
    try:
        scheme, phrase = uri.split('://')
    except ValueError:
        scheme = 'glob'
        phrase = uri

    try:
        finder = registry.get(scheme)
    except KeyError:
        return []
    else:
        return finder.search(phrase)
