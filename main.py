"""Keep your music organized.

Usage:
  main.py [-d <PATH>] add (song | group | album)
  main.py [-d <PATH>] playlist <name> [-s <song>]...
  main.py [-d <PATH>] list songs <genre>
  main.py [-d <PATH>] list song  <name>
  main.py [-d <PATH>] list group <name>
  main.py [-d <PATH>] list album <name>
  main.py [-d <PATH>] search song <name>
  main.py -h | --help
  main.py --version

Options:
  -h --help             Show this screen.
  -d --database <PATH>  Path to the local storage [default: muziek.db].
  -s --song <song>      Song to add to the playlist.
  --version             Show version.
"""

import docopt

from libs import __version__, console_interface as cli
from libs.database import DBMuziek


if __name__ == "__main__":
    args = docopt.docopt(__doc__, version=__version__)

    with DBMuziek(args['--database']) as db:
        if args['add']:
            if args['song']:
                cli.add_song(db)
            elif args['group']:
                cli.add_group(db)
            elif args['album']:
                cli.add_album(db)

        elif args['list']:
            if args['songs']:
                cli.list_songs(db, args['<genre>'])
            elif args['song']:
                cli.list_song(db, args['<name>'])
            elif args['group']:
                cli.list_group(db, args['<name>'])
            elif args['album']:
                cli.list_album(db, args['<name>'])

        elif args['playlist']:
            if len(args['--song']) == 0:
                cli.list_playlist(db, args['<name>'])
            else:
                cli.add_song_playlist(db, args['<name>'], args['--song'])

        elif args['search']:
            if args['song']:
                cli.search_song(db, args['<name>'])
