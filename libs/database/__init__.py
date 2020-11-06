import sqlite3


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
    if not table_exists(con, 'songs'):
        execute(con, 'CREATE TABLE songs')
    if not table_exists(con, 'groups'):
        execute(con, 'CREATE TABLE groups')
    if not table_exists(con, 'playlists'):
        execute(con, 'CREATE TABLE playlists')
    if not table_exists(con, 'albums'):
        execute(con, 'CREATE TABLE albums')


def table_exists(con: Connection, name: str) -> int:
    result = execute(con, "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return result.fetchone()[0]
