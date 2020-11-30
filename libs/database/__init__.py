import sqlite3
from typing import Optional, List

from . import db_queries


def query_append(prefix: str, suffix: str, *args):
    """This function generates an SQL query out of smaller blocks, only adding those that are needed.

    :author: Carlos
    :param prefix: What the query will start with, so the columns and tables.
    :param suffix: What the query will end with, for example a LIMIT or OFFSET.
    :param args: A tuple containing the query block and the value that fits in that query,
                 if the value is None it's ignored.
    :return: A tuple with the custom query and a list of values, where the None values have been removed.
    """
    parameters = []
    appends = []

    for (query, val) in args:
        if val is not None:
            parameters.append(val)
            appends.append(query)

    appendix = ' AND '.join(appends)

    if appendix:
        prefix = f'{prefix} WHERE {appendix}'
    query = f'{prefix} {suffix};'

    return query, parameters


def fuzy(string: Optional[str]):
    """This function transforms a normal string into an SQL fuzy search string.

    :param string: the input string.
    :return: The fuzy string the input string is empty/None.
    """
    return f'%{string.lower()}%' if string else None


class DBMuziek:
    def __init__(self, path: str):
        """This class represents our database connection.

        :param path: The path to the database file.
        """
        self._connection: Optional[sqlite3.Connection] = None
        self._path: str = path

    def __enter__(self):
        """Starts the connection to the database file, and verifies the tables needed are there.

        :author: Mathieu
        """
        self.connect()
        self.validate_tables()
        return self

    def __exit__(self, *args):
        """Closes the connection to the database file.

        :author: Mathieu
        """
        self.disconnect()

    def connect(self):
        """Starts the connection to the database file with the path stored.

         :author: Carlos
        """
        self._connection = sqlite3.connect(self._path)
        self._connection.row_factory = sqlite3.Row

    def disconnect(self):
        """Closes the connection to the database file.

        :author: Mathieu
        """
        self._connection.close()
        self._connection = None

    @property
    def connection(self):
        return self._connection

    def execute(self, query: str, parameters=()) -> sqlite3.Cursor:
        """Executes an sql query, replacing the parameters.

        :param query: The query to execute.
        :param parameters: The parameters to replace within the query.
        :return: A database cursor.
        """
        return self._connection.execute(query, parameters)

    def commit(self):
        """Commits a database transaction.

        :author: Mathieu
        """
        self._connection.commit()

    def validate_tables(self):
        """Checks if the expected tables exist in the database and creates them if they don't.

        :author: Carlos
        """
        if not self.foreign_keys():
            self.execute(db_queries.foreign_keys_enable)

        if not self.table_exists('groups'):
            self.execute(db_queries.create_groups)

        if not self.table_exists('songs'):
            self.execute(db_queries.create_songs)
        if not self.table_exists('songFeaturing'):
            self.execute(db_queries.create_songFeaturing)

        if not self.table_exists('playlists'):
            self.execute(db_queries.create_playlists)
        if not self.table_exists('playlistSongs'):
            self.execute(db_queries.create_playlistSongs)

        if not self.table_exists('albums'):
            self.execute(db_queries.create_albums)
        if not self.table_exists('albumSongs'):
            self.execute(db_queries.create_albumSongs)

        if not self.table_exists('settings'):
            self.execute(db_queries.create_settings)

    def table_exists(self, name: str) -> int:
        """Checks if a table exist in the database.

        :param name: name of the table to check.
        :return: 1 if it exists, 0 if it doesn't.
        """
        result = self.execute(db_queries.table_exists, (name,))
        return result.fetchone()[0]

    def foreign_keys(self) -> int:
        """Checks if foreign_keys are enabled in sqlite.

        :return: 1 if enabled, 0 if disabled.
        """
        result = self.execute(db_queries.foreign_keys)
        return result.fetchone()[0]

    def count_songs(self, filters: dict):
        """Returns the amount of songs, after being filtered.

        :param filters: Filters the songs need to fit to be counted.
        :return: The amount of songs.
        """
        genre = (db_queries.append_genre, filters["genre"])
        name = (db_queries.append_name, fuzy(filters["name"]))
        group = (db_queries.append_group, fuzy(filters["group"]))
        query, params = query_append(db_queries.count_songs, "", genre, name, group)

        return self.execute(query, params).fetchone()[0]

    def get_playlist(self, name: str):
        """Obtains a playlist from the database based on its name.

        :param name: The name of the playlist.
        :return: A Row if the playlist exists, None if it doesn't
        """
        return self.execute(db_queries.get_playlist, (name,)).fetchone()

    def get_song(self, name: str):
        """Obtains a song from the database based on its name.

        :param name: The name of the song.
        :return: A Row if the song exists, None if it doesn't
        """
        return self.execute(db_queries.get_song, (name,)).fetchone()

    """
    TODO: A get_song that accepts a song_name and a group_id, to prevent collisions.
    """

    def get_songs(self, filters: dict, offset: int = 0, limit: int = 50):
        """Obtains a defined amount of songs, after being filtered.

        :param filters: The filters the songs need to fit.
        :param offset: The offset in the database query.
        :param limit: The lmimit in the database query.
        :return: An array of Rows
        """
        genre = (db_queries.append_genre, filters["genre"])
        name = (db_queries.append_name, fuzy(filters["name"]))
        group = (db_queries.append_group, fuzy(filters["group"]))
        query, params = query_append(db_queries.get_songs, db_queries.paging, genre, name, group)

        return self.execute(query, (*params, limit, offset)).fetchall()

    def get_group(self, name: str, verbose: bool = False):
        """Obtains a group from the database based on its name,
        will return even more info about it if requested.

        :param name: The name of the group.
        :param verbose: If more info should be provided.
        :return: A Row if the song exists, None if it doesn't.
                 If verbose the counts of songs and albums will also be provided.
        """
        group_query = self.execute(db_queries.get_group, (name,)).fetchone()
        if not verbose:
            return group_query
        elif group_query:
            songs = self.execute(db_queries.count_group_songs, (group_query["group_id"],)).fetchone()["count"]
            albums = self.execute(db_queries.count_group_albums, (group_query["group_id"],)).fetchone()["count"]
            return group_query, songs, albums

    def get_album(self, name: str, verbose: bool = False):
        """Obtains an album from the database based on its name,
        will return even more info about it if requested.

        :param name: The name of the album.
        :param verbose: If more info should be provided.
        :return: A Row if the song exists, None if it doesn't.
                 If verbose a list of Rows with the songs in the album will be also provided.
        """
        album_query = self.execute(db_queries.get_album, (name,)).fetchone()
        if not verbose:
            return album_query
        elif album_query:
            songs = self.execute(db_queries.get_songs_album, (album_query["album_id"],)).fetchall()
            return album_query, songs

    def add_song_playlist(self, playlist_id: int, song_id: int):
        """Adds an existing song to an existing playlist.

        :param playlist_id: The id of the playlist.
        :param song_id: The id of the song.
        :return: A database cursor.
        """
        return self.execute(db_queries.add_song_playlist, (playlist_id, song_id))

    def get_playlist_songs(self, playlist_id: int):
        """Returns the songs contained in a playlist.

        :param playlist_id: The id of the playlist.
        :return: A list of Rows with the songs in the playlist.
        """
        return self.execute(db_queries.get_playlist_data, (playlist_id,)).fetchall()

    def create_playlist(self, name: str, author: str) -> int:
        """Creates a new playlist in the database.

        :param name: Name for the playlist.
        :param author: The user that created the playlist.
        :return: The id of the created playlist
        """
        return self.execute(db_queries.create_playlist, (name, author)).lastrowid

    def create_group(self, name: str, members: List[str]) -> int:
        """Creates a new group in the database.

        :param name: Name of the group.
        :param members: List of members of the group.
        :return: The if of the created group.
        """
        return self.execute(db_queries.create_group, (name, ','.join(members))).lastrowid

    def update_group(self, group_id: int, members: List[str]):
        """Updates the information stored for a group in the database.

        :param group_id: The id of group to update.
        :param members: The members of the group.
        :return: A database cursor.
        """
        return self.execute(db_queries.update_group, (','.join(members), group_id))

    def create_song(self, name: str, link: str, genre: str, group_id: int, featuring: List[int]) -> int:
        song_id = self.execute(db_queries.create_song, (name, link, genre, group_id)).lastrowid

        for featuring_id in featuring:
            self.execute(db_queries.add_song_featuring, (song_id, featuring_id))

        return song_id

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

    def get_setting(self, key: str, default: str = None) -> str:
        row = self.execute(db_queries.get_setting, (key,)).fetchone()
        if row is None:
            return default

        return row['value']

    def set_setting(self, key: str, value: str):
        self.execute(db_queries.set_setting, (key, str(value)))
