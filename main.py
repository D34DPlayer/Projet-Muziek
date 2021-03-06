"""Keep your music organized.

Usage:
  muziek [-d <PATH>]
  muziek [-d <PATH>] add (song | group | album)
  muziek [-d <PATH>] playlist <name> [-D | -e | -i | -s <song>...]
  muziek [-d <PATH>] list songs [-g <genre>] [-n <name>] [-G group]
  muziek [-d <PATH>] list group <name>
  muziek [-d <PATH>] list album <name>
  muziek [-d <PATH>] list (playlists | groups | albums)
  muziek [-d <PATH>] download song <name>
  muziek [-d <PATH>] youtube list [<name>]
  muziek [-d <PATH>] youtube import <name>
  muziek [-d <PATH>] youtube export <name>
  muziek -h | --help
  muziek --version

Options:
  -h --help             Show this screen.
  -d --database <PATH>  Path to the local storage [default: muziek.db].
  -s --song <song>      Song(s) to add to the playlist.
  -D --download         Download all the songs included in the playlist.
  -e --export           Exports the playlist.
  -i --import           Imports a playlist with the provided name.
  -g --genre <genre>    Filter the songs listed based on the genre.
  -G --group <group>    Filter the songs listed based on the group's name.
  -n --name <name>      Filter the songs listed based on the song's name.
  --version             Show version.
"""

import docopt

from libs import __version__
from libs import console_interface as cli
from libs.database import DBMuziek
from libs.logger import setup_logger

if __name__ == "__main__":
    setup_logger()

    args = docopt.docopt(__doc__, version=__version__)
    filters = {k.lstrip('-'): v for k, v in args.items() if k.startswith('--')}

    with DBMuziek(args['--database']) as db:
        try:
            if args['add']:
                if args['song']:
                    cli.add_song(db)
                elif args['group']:
                    cli.add_group(db)
                elif args['album']:
                    cli.add_album(db)

            elif args['youtube']:  # overwrite `list` command
                if args['list']:
                    cli.list_yt_playlist(db, args['<name>'])
                elif args['import']:
                    cli.import_from_yt(db, args['<name>'])
                elif args['export']:
                    cli.export_to_yt(db, args['<name>'])

            elif args['list']:
                if args['songs']:
                    cli.list_songs(db, filters)
                elif args['group']:
                    cli.list_group(db, args['<name>'])
                elif args['album']:
                    cli.list_album(db, args['<name>'])
                elif args['playlists']:
                    cli.list_playlists(db)
                elif args['albums']:
                    cli.list_albums(db)
                elif args['groups']:
                    cli.list_groups(db)

            elif args['playlist']:
                if args['--download']:
                    cli.download_playlist(db, args["<name>"])
                if args['--import']:
                    cli.import_playlist(db, args['<name>'])
                elif args['--export']:
                    cli.export_playlist(db, args['<name>'])
                elif len(args['--song']) == 0:
                    cli.list_playlist(db, args['<name>'])
                else:
                    cli.add_song_playlist(db, args['<name>'], args['--song'])

            elif args['download']:
                if args['song']:
                    cli.download_song(db, args['<name>'])

            else:
                from libs import graphical_interface as gui
                gui.run(db)

        except KeyboardInterrupt:
            print('Exiting...')
