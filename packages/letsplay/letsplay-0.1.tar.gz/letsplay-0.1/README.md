# letsplay
An extensible music player wbrary ritten in Python

## Features

  * thin wrapper around any media player (mplayer as default)
  * possibility to bind to any user interface (via extensions)
  * local and remote files (multiple schemes supported)
  * media finders API
  * D-Bus `org.mpris.MediaPlayer2` integration
  * extensible via plugins
  
## Quickstart (Python API)

```
import letsplay as lp

player = lp.init()
player.load(lp.find('/path/to/music/files/*.mp3'))
player.play()
```

### Expose D-bus interface

Same as above plus:

```
lp.mpris.register_mpris_service(player)
loop = lp.mpris.create_glib_loop()
loop.run()
```

### Destroying the player

Remember to destroy the player. It is required for cleaning up.

```
try:
    loop.run()
finally:
    player.destroy()
```

## License

GPL3
