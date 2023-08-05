import taglib
from .utils import title_from_path


class Song(object):
    def __init__(
            self, path, title=None, album=None, artist=None, duration=None,
            genres=None):
        self.path = path
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.genres = genres

    def __duration__(self):
        return self.duration

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.path)

    @classmethod
    def local(cls, path):
        return localsong(path, cls=cls)


def localsong(path, cls=Song):
    x = taglib.File(path)
    title = x.tags.get('TITLE')
    album = x.tags.get('ALBUM')
    artist = x.tags.get('ARTIST')
    genres = x.tags.get('GENRE')
    return Song(
            path=path,
            title=title[0] if title else title_from_path(path),
            album=album[0] if album else None,
            artist=artist[0] if artist else None,
            genres=genres,
            duration=x.length
            )
