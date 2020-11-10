from ..database import DBMuziek
from argparse import Namespace


def cli_add(db: DBMuziek, arguments: Namespace):
    if arguments.TYPE == 'song':
        add_song(db)
    elif arguments.TYPE == 'album':
        add_album(db)
    else:
        add_group(db)


def cli_list(db: DBMuziek, arguments: Namespace):
    if arguments.TYPE == 'song':
        list_song(db, arguments.NAME)
    elif arguments.TYPE == 'album':
        list_album(db, arguments.NAME)
    else:
        list_group(db, arguments.NAME)


def cli_playlist(db: DBMuziek, arguments: Namespace):
    if arguments.song:
        add_song_playlist(db, arguments.NAME, arguments.song)
    else:
        list_playlist(db, arguments.NAME)


def add_song(db: DBMuziek):
    return True


    return True
def add_song_playlist(db: DBMuziek, name: str, songs: list[str]):


def add_group(db: DBMuziek):
    return True


def add_album(db: DBMuziek):
    return True


def list_song(db: DBMuziek, name: str):
    return True


def list_group(db: DBMuziek, name: str):
    return True


def list_album(db: DBMuziek, name: str):
    return True


def list_playlist(db: DBMuziek, name: str):
    return True
