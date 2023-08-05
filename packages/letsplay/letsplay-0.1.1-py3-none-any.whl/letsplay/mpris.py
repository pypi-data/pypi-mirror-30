import dbus
import dbus.service
import dbus.exceptions
import threading
import sys

from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from .utils import duration


def create_dbus_loop():
    return DBusGMainLoop()


def acquire_bus(player, dbus_loop):
    try:
        return dbus.service.BusName(
            'org.mpris.MediaPlayer2.letsplay',
            bus=dbus.SessionBus(mainloop=dbus_loop))
    except dbus.exceptions.NameExistsException:
        print("DBus service is already running")
        raise


def run_loop(loop):
    try:
        loop.run()
    finally:
        loop.quit()


def register_mpris_service(player):
    dbus_loop = create_dbus_loop()
    bus = acquire_bus(player, dbus_loop)
    return Mpris2Service(player, bus)  # NOQA


def create_glib_loop(player):
    return GLib.MainLoop()


def main(player):
    service = register_mpris_service(player)
    loop = create_glib_loop(player)

    def start_loop_thread():
        print("Start dbus loop thread")
        try:
            loop.run()
        except KeyboardInterrupt:
            pass
        finally:
            loop.quit()
        print("End dbus loop thread")

    t = threading.Thread(target=start_loop_thread)
    t.start()
    return service


class Mpris2Service(dbus.service.Object):
    def __init__(self, player, bus):
        super().__init__(bus, '/org/mpris/MediaPlayer2')
        self.player = player
        self.props_getters = {
                'org.mpris.MediaPlayer2': self.get_root_properties,
                'org.mpris.MediaPlayer2.Player': self.get_player_properties,
                }

        def player_status_updater(dbus_prop, attr):
            def updater(player):
                self.update_property(
                    'org.mpris.MediaPlayer2.Player',
                    dbus_prop, getattr(player, attr, None))
            return updater

        def update_playback_status():
            self.update_property(
                'org.mpris.MediaPlayer2.Player',
                'PlaybackStatus', self.get_playback_status())

        def update_on_track_change():
            metadata = self.get_current_track_metadata()

            if metadata:
                self.update_property(
                        'org.mpris.MediaPlayer2.Player', 'Metadata', metadata)

        def update_all_props():
            self.PropertiesChanged(
                    'org.mpris.MediaPlayer2.Player',
                    self.get_player_properties(), [])

        self.player.on('play', update_playback_status)
        self.player.on('stop', update_playback_status)
        self.player.on('pause', update_playback_status)
        self.player.on('next', update_on_track_change)
        self.player.on('previous', update_on_track_change)
        self.player.on('load', update_all_props)

    @dbus.service.method(
            'org.freedesktop.DBus.Properties',
            in_signature='ss', out_signature='v')
    def Get(self, iface, what):
        print('Get', iface, what)

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='ssv')
    def Set(self, iface, what, value):
        print('Set', iface, what)

    def get_playback_status(self):
        player = self.player

        if player.is_playing:
            status = 'Playing'
        elif player.is_paused:
            status = 'Paused'
        else:
            status = 'Stopped'
        return status

    def get_current_track_metadata(self):
        player = self.player

        if player.current:
            data = {
                'mpris:trackid': dbus.ObjectPath(
                    '/Current/%s' % player.current_index, variant_level=1),
                'mpris:length': dbus.Int64(
                    duration(player.current)*1000000, variant_level=1),
                }
            if player.current.title:
                data.update({
                    'xesam:title': dbus.String(
                        player.current.title, variant_level=1),
                })
            if player.current.artist:
                data.update({
                    'xesam:artist': dbus.Array(
                        [player.current.artist], 's', 1),
                })
            if player.current.album:
                data.update({
                    'xesam:album': dbus.String(
                        player.current.album, variant_level=1),
                })
            return data
        else:
            return None

    def update_property(self, iface, what, value):
        self.PropertiesChanged(iface, {what: value}, [])

    @dbus.service.method(
            'org.freedesktop.DBus.Properties',
            in_signature='s', out_signature='a{sv}')
    def GetAll(self, iface):
        getter = self.props_getters.get(iface)
        if getter:
            return getter()
        else:
            return {}

    @dbus.service.signal(
            'org.freedesktop.DBus.Properties', signature='sa{sv}as')
    def PropertiesChanged(self, iface, changed, invalidated):
        pass

    def get_root_properties(self):
        return {
                'CanQuit': True,
                'Fullscreen': False,
                'CanSetFullscreen': False,
                'CanRaise': False,
                'HasTrackList': False,
                'Identity': 'LetsPlay',
                'SupportedUriSchemes': dbus.Array(['file', 'glob'], 's', 1),
                }

    def get_player_properties(self):
        player = self.player
        metadata = self.get_current_track_metadata()
        props = {
                'PlaybackStatus': self.get_playback_status(),
                'LoopStatus': 'Playlist' if player.repeat else 'None',
                'Rate': 1.0,
                'Shuffle': player.shuffle,
                'Volume': player.volume,
                'MinimumRate': 1.0,
                'MaximumRate': 1.0,
                'CanGoNext': player.has_next(),
                'CanGoPrevious': player.has_previous(),
                'CanControl': True,
                'CanPause': True,
                'CanPlay': True,
                'CanSeek': False,
                }
        if metadata:
            props['Metadata'] = metadata
        return props

    @dbus.service.method('org.mpris.MediaPlayer2')
    def Raise(self):
        pass

    @dbus.service.method('org.mpris.MediaPlayer2')
    def Quit(self):
        sys.exit(0)

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Next(self):
        self.player.next()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Previous(self):
        self.player.previous()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Pause(self):
        self.player.pause()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Stop(self):
        self.player.stop()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Play(self):
        self.player.play()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def PlayPause(self):
        if self.player.is_playing:
            self.player.pause()
        else:
            self.player.play()
