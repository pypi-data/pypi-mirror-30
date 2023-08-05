import observable
import random


class Player(object):
    def __init__(self, songs=None, shuffle=False, repeat=True):
        self.songs = list(songs or [])
        self.shuffle = shuffle
        self.repeat = repeat
        self.current = None
        self.current_index = None
        self.is_playing = False
        self.is_paused = False
        self._ev = observable.Observable()
        self.volume = 1.0

    def load(self, songs):
        self.songs = list(songs)
        self._ev.trigger('load')
        self.reset()
        self.next()

    def goto(self, index):
        self.current_index = index
        self.current = self.songs[self.current_index]
        self._ev.trigger('change')

    def stop(self):
        self.current_index = None
        self.current = None
        self.is_playing = False
        self.is_paused = False
        self._ev.trigger('stop')

    def clear(self):
        self.songs = []
        self._ev.trigger('clear')

    def play(self):
        if not self.current:
            self.next()
        if self.current:
            self.is_playing = True
            self.is_paused = False
            self._ev.trigger('play')

    def pause(self):
        if self.current:
            self.is_playing = False
            self.is_paused = True
            self._ev.trigger('pause')

    def reset(self):
        if self.shuffle:
            random.shuffle(self.songs)
        self._ev.trigger('reset')

    def has_next(self):
        if not self.songs:
            return False

        if self.current_index is None:
            return True

        if self.current_index < len(self.songs) or self.repeat:
            return True

        return False

    def has_previous(self):
        if not self.songs:
            return False

        if self.current_index is None and self.repeat:
            return True

        if self.current_index > 0 or self.repeat:
            return True

        return False

    def next(self):
        if not self.has_next():
            return

        idx = 0 if self.current_index is None else self.current_index + 1

        try:
            self.goto(idx)
        except IndexError:
            if self.repeat:
                self.reset()
                self.goto(0)
            else:
                self.stop()

        if self.current:
            self._ev.trigger('next')
        return self.current

    def previous(self):
        if not self.has_previous():
            return

        idx = len(self.songs)-1 if (
                self.current_index is None) else self.current_index - 1

        try:
            self.goto(idx)
        except IndexError:
            if self.repeat:
                self.reset()
                self.goto(len(self.songs)-1)
            else:
                self.stop()
        if self.current:
            self._ev.trigger('previous')
        return self.current

    def on(self, *args, **kw):
        return self._ev.on(*args, **kw)

    def off(self, *args, **kw):
        return self._ev.off(*args, **kw)

    def once(self, *args, **kw):
        return self._ev.once(*args, **kw)

    def destroy(self):
        self.stop()
        self.clear()
        self._ev.trigger('destroy')
