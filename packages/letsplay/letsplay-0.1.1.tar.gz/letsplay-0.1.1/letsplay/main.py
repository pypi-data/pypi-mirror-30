from .output import MplayerOutput
from . import mpris
from . import Player


def init():
    output = MplayerOutput()
    player = Player()

    def play_via_mplayer():
        output.load(player.current.path)
        if player.is_playing:
            output.play()

    def play_next_on_stop():
        if player.is_playing:
            player.next()

    output.on('stop', play_next_on_stop)

    player.on('change', play_via_mplayer)
    player.on('pause', output.pause)
    player.on('stop', output.pause)
    player.on('play', output.play)
    player.on('destroy', output.destroy)

    return player


def run_cli():
    import argparse
    from . import find, __version__

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'phrase', help='Search query (defaults to glob pattern)')
    parser.add_argument(
        '--version', action='version', version=__version__)

    opts = parser.parse_args()

    player = init()
    player.load(find(opts.phrase))
    player.play()

    mpris.register_mpris_service(player)
    loop = mpris.create_glib_loop(player)

    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        player.destroy()
