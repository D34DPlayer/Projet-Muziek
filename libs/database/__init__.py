import sqlite3
from typing import Optional, List

from . import db_queries


class DBMuziek:
    def __init__(self, path: str):
        self._connection: Optional[sqlite3.Connection] = None
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
            self.execute(db_queries.create_groups)

        if not self.table_exists('songs'):
            self.execute(db_queries.create_songs)

        if not self.table_exists('playlists'):
            self.execute(db_queries.create_playlists)
        if not self.table_exists('playlistSongs'):
            self.execute(db_queries.create_playlistSongs)

        if not self.table_exists('albums'):
            self.execute(db_queries.create_albums)
        if not self.table_exists('albumSongs'):
            self.execute(db_queries.create_albumSongs)

    def table_exists(self, name: str) -> int:
        result = self.execute(db_queries.table_exists, (name,))
        return result.fetchone()[0]

    def foreign_keys(self) -> int:
        result = self.execute(db_queries.foreign_keys)
        return result.fetchone()[0]

    def get_playlist(self, name: str):
        return self.execute(db_queries.get_playlist, (name,)).fetchone()

    def get_song(self, name: str):
        return self.execute(db_queries.get_song, (name,)).fetchone()

    def get_group(self, name: str):
        return self.execute(db_queries.get_group, (name,)).fetchone()

    def add_song_playlist(self, playlist_id: int, song_id: int):
        return self.execute(db_queries.add_song_playlist, (playlist_id, song_id))

    def get_playlist_data(self, playlist_id: int):
        return self.execute(db_queries.get_playlist_data, (playlist_id,)).fetchall()

    def create_playlist(self, name: str, author: str) -> int:
        return self.execute(db_queries.create_playlist, (name, author)).lastrowid

    def create_group(self, name: str, members: List[str]) -> int:
        return self.execute(db_queries.create_group, (name, ','.join(members))).lastrowid

    def update_group(self, group_id: int, members: List[str]):
        return self.execute(db_queries.update_group, (','.join(members), group_id))

    def create_song(self, name: str, link: str, genre: str, group_id: int) -> int:
        return self.execute(db_queries.create_song, (name, link, genre, group_id)).lastrowid

    def update_song(self, song_id: int, link: str, genre: str, group_id: int):
        return self.execute(db_queries.update_song, (link, genre, group_id, song_id))
