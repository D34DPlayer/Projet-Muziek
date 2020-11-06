from .. import database as db


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
