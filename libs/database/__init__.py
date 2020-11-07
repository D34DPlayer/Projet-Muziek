import sqlite3
from . import db_queries


Connection = sqlite3.Connection


def connect(path: str) -> Connection:
    con = sqlite3.connect(path)
    validate_tables(con)
    return con


def disconnect(con: Connection):
    con.close()


def execute(con: Connection, query: str, parameters=()) -> sqlite3.Cursor:
    return con.execute(query, parameters)


def validate_tables(con: Connection):
    if not foreign_keys(con):
        execute(con, db_queries.foreign_keys_enable)

    if not table_exists(con, 'groups'):
        execute(con, db_queries.groups)

    if not table_exists(con, 'songs'):
        execute(con, db_queries.songs)

    if not table_exists(con, 'playlists'):
        execute(con, db_queries.playlists)
    if not table_exists(con, 'playlistSongs'):
        execute(con, db_queries.playlistSongs)

    if not table_exists(con, 'albums'):
        execute(con, db_queries.albums)
    if not table_exists(con, 'albumSongs'):
        execute(con, db_queries.albumSongs)


def table_exists(con: Connection, name: str) -> int:
    result = execute(con, db_queries.table_exists, (name,))
    return result.fetchone()[0]


def foreign_keys(con: Connection) -> int:
    result = execute(con, db_queries.foreign_keys)
    return result.fetchone()[0]
