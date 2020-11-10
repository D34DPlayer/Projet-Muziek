import sqlite3

from . import db_queries


class DBMuziek:
    def __init__(self, path: str):
        self._connection: sqlite3.Connection = None
        self._path: str = path

    def __enter__(self):
        self.connect()
        self.validate_tables()
        return self

    def __exit__(self, *args):
        self.disconnect()

    def connect(self):
        self._connection = sqlite3.connect(self._path)

    def disconnect(self):
        self._connection.close()
        self._connection = None

    def execute(self, query: str, parameters=()) -> sqlite3.Cursor:
        return self._connection.execute(query, parameters)

    def commit(self):
        self._connection.commit()

    def validate_tables(self):
        if not self.foreign_keys():
            self.execute(db_queries.foreign_keys_enable)

        if not self.table_exists('groups'):
            self.execute(db_queries.groups)

        if not self.table_exists('songs'):
            self.execute(db_queries.songs)

        if not self.table_exists('playlists'):
            self.execute(db_queries.playlists)
        if not self.table_exists('playlistSongs'):
            self.execute(db_queries.playlistSongs)

        if not self.table_exists('albums'):
            self.execute(db_queries.albums)
        if not self.table_exists('albumSongs'):
            self.execute(db_queries.albumSongs)

    def table_exists(self, name: str) -> int:
        result = self.execute(db_queries.table_exists, (name,))
        return result.fetchone()[0]

    def foreign_keys(self) -> int:
        result = self.execute(db_queries.foreign_keys)
        return result.fetchone()[0]
