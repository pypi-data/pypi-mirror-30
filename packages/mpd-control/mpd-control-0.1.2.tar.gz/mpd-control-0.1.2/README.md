Basic python program to control MPD from command line.

Requires [python-mpd2](https://github.com/Mic92/python-mpd2)

    pip install --user python-mpd2

Basic help output:

    $ python mpd-control.py --help             
    usage: mpd-control.py [-h] [-p] [-S] [-n] [-s] [-v VOLUME] [-i IP]

    Control playback on your mpd server.

    optional arguments:
      -h, --help            show this help message and exit
      -p, --pause           Toggles playback
      -S, --song            Prints info on the current song
      -n, --next            Next song
      -s, --shuffle         Toggles shuffle
      -v VOLUME, --volume VOLUME
                            Changes the volume to given values, 0-100
      -i IP, --ip IP        Specify an IP address, defaults to 'localhost'
