from .. import database as db
from argparse import Namespace


def cli_add(connection: db.Connection, arguments: Namespace):
    if arguments.TYPE == 'song':
        add_song(connection)
    elif arguments.TYPE == 'album':
        add_album(connection)
    else:
        add_group(connection)


def cli_list(connection: db.Connection, arguments: Namespace):
    if arguments.TYPE == 'song':
        list_song(connection, arguments.NAME)
    elif arguments.TYPE == 'album':
        list_album(connection, arguments.NAME)
    else:
        list_group(connection, arguments.NAME)


def cli_playlist(connection: db.Connection, arguments: Namespace):
    if arguments.song:
        add_song_playlist(connection, arguments.NAME, arguments.song)
    else:
        list_playlist(connection, arguments.NAME)


def add_song(con: db.Connection):
    return True


def add_song_playlist(con: db.Connection, name: str, songs):
    return True


def add_group(con: db.Connection):
    return True


def add_album(con: db.Connection):
    return True


def list_song(con: db.Connection, name: str):
    return True


def list_group(con: db.Connection, name: str):
    return True


def list_album(con: db.Connection, name: str):
    return True


def list_playlist(con: db.Connection, name: str):
    return True
