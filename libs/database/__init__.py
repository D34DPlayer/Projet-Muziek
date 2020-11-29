import sqlite3
from typing import Optional, List

from . import db_queries


def query_append(prefix: str, suffix: str, *args):
    parameters = []
    appends = []

    for (query, val) in args:
        if val:
            parameters.append(val)
            appends.append(query)

    appendix = ' AND '.join(appends)

    if appendix:
        prefix = f'{prefix} WHERE {appendix}'
    query = f'{prefix} {suffix};'

    return query, parameters


def fuzy(string):
    return f'%{string.lower()}%' if string else None


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
        self._connection.row_factory = sqlite3.Row

    def disconnect(self):
        self._connection.close()
        self._connection = None

    @property
    def connection(self):
        return self._connection

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

    def count_songs(self, filters: dict):
        genre = (db_queries.append_genre, filters["genre"])
        name = (db_queries.append_name, fuzy(filters["name"]))
        group = (db_queries.append_group, fuzy(filters["group"]))
        query, params = query_append(db_queries.count_songs, "", genre, name, group)

        return self.execute(query, params).fetchone()[0]

    def get_playlist(self, name: str):
        return self.execute(db_queries.get_playlist, (name,)).fetchone()

    def get_song(self, name: str):
        return self.execute(db_queries.get_song, (name,)).fetchone()

    def get_songs(self, filters: dict, offset: int = 0, limit: int = 50):
        genre = (db_queries.append_genre, filters["genre"])
        name = (db_queries.append_name, fuzy(filters["name"]))
        group = (db_queries.append_group, fuzy(filters["group"]))
        query, params = query_append(db_queries.get_songs, db_queries.paging, genre, name, group)

        return self.execute(query, (*params, limit, offset)).fetchall()

    def get_group(self, name: str):
        return self.execute(db_queries.get_group, (name,)).fetchone()

    def get_album(self, name: str):
        return self.execute(db_queries.get_album, (name,)).fetchone()

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

    def create_album(self, name: str, songs: List[int], group_id: int) -> int:
        album_id = self.execute(db_queries.create_album, (name, group_id)).lastrowid
        for song_id in songs:
            self.execute(db_queries.add_song_album, (album_id, song_id))
        return album_id

    def update_album(self, album_id: int, songs: List[int]):
        self.execute(db_queries.delete_album_songs, (album_id,))
        for song_id in songs:
            self.execute(db_queries.add_song_album, (album_id, song_id))
