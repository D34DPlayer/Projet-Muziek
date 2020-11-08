import argparse
import libs.database as db
import libs.console_interface as cli


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='SoundsGood', description="Keep your music organized.")
    subparsers = parser.add_subparsers(help='Action to perform')
    parser.add_argument('-d', '--database', help='Path to the local storage', default='./muziek.db')

    parser_add = subparsers.add_parser('add', help='Add something to the local storage')
    parser_playlist = subparsers.add_parser('playlist', help='Add a song to a playlist')
    parser_list = subparsers.add_parser('list', help='Add something to the local storage')

    parser_add.add_argument('TYPE', help='What to add to the local storage', choices=['song', 'group', 'album'])
    parser_add.set_defaults(func=cli.cli_add)

    parser_list.add_argument('TYPE', help='What to see from the local storage', choices=['song', 'group', 'album'])
    parser_list.add_argument('NAME', help='Name of that type')
    parser_list.set_defaults(func=cli.cli_list)

    parser_playlist.add_argument('NAME', help='Name of that playlist')
    parser_playlist.add_argument('-s', '--song', help='Song to add to the playlist', action='append')
    parser_playlist.set_defaults(func=cli.cli_playlist)

    args = parser.parse_args()

    if 'func' not in args:
        parser.print_usage()
        exit()

    con = db.connect(args.database)

    args.func(con, args)

    db.disconnect(con)
