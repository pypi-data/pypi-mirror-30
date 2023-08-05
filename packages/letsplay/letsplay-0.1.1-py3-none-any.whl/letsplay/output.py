import observable
import time
import threading


class BaseOutput(object):
    def __init__(self):
        self._ev = observable.Observable()

    def on(self, *args, **kw):
        return self._ev.on(*args, **kw)

    def off(self, *args, **kw):
        return self._ev.on(*args, **kw)

    def play(self):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def load(self, path):
        raise NotImplementedError

    def trigger_playback_start(self):
        self._ev.trigger('start')

    def trigger_playback_stop(self):
        self._ev.trigger('stop')

    def trigger_file_change(self):
        self._ev.trigger('filechange')

    def destroy(self):
        pass


class MplayerOutput(BaseOutput):
    def __init__(self):
        super().__init__()
        import mplayer
        self._mp = mplayer.Player()
        self._loaded = False
        self._playing = False
        self._thread_canceller = threading.Event()

        def playback_observer():
            while True:
                if self._thread_canceller.is_set():
                    return
                new_loaded = bool(self._mp.stream_length)
                if not self._loaded == new_loaded:
                    self._loaded = new_loaded
                    self.trigger_file_change()

                is_playing = not self._mp.paused
                if not self._playing == is_playing:
                    self._playing = is_playing
                    if is_playing:
                        self.trigger_playback_start()
                    else:
                        self.trigger_playback_stop()
                time.sleep(1)

        t = threading.Thread(target=playback_observer)
        t.daemon = True
        t.start()

    def play(self):
        if not self._mp.is_alive():
            self._mp.spawn()
        if self._mp.paused:
            self._mp.pause()

    def pause(self):
        if not self._mp.is_alive():
            self._mp.spawn()
        if not self._mp.paused:
            self._mp.pause()

    def load(self, path):
        self._mp.loadfile(path)

    def destroy(self):
        super().destroy()
        self._thread_canceller.set()
