import sqlite3
from functools import wraps
from typing import List, Optional

from ..logger import get_logger
from . import db_queries

logger = get_logger("db")


def format_duration(duration: int = None):
    if duration is None:
        return '??:??'

    return '{}:{}'.format(*divmod(duration, 60))


def query_append(prefix: str, suffix: str, *args):
    """This function generates an SQL query out of smaller blocks, only adding those that are needed.

    :author: Carlos
    :param prefix: What the query will start with, so the columns and tables.
    :param suffix: What the query will end with, for example a LIMIT or OFFSET.
    :param args: A tuple containing the query block and the value that fits in that query,
                 if the value is None it's ignored.
    :PRE: _
    :POST: Returns a tuple with the custom query and a list of values, where the None values have been removed.
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
    :PRE: _
    :POST: Returns the fuzy string the input string is empty/None.
    """
    return f'%{string.lower()}%' if string else None


def db_error(f_name: str, e: Exception, msg: str = ""):
    """

    :param f_name: The action that caused the error.
    :param e: The error message.
    :param msg: Addional message. Optional.
    :PRE: f_name must be a fuction name with "_" between the words
    :POST: The error is logged.
    """
    logger.error(f"""There was an error when trying to {f_name.replace('_', ' ')}.
    {e}
    {msg}""")


def db_query(f):
    """Decorator that handles database errors properly.

    :author: Carlos
    :param f: Funtion to be decorated.
    :PRE: f must execute a sql query
    :POST: If there's a sqlite error it will be logged and an empty value will be returned.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except sqlite3.IntegrityError as e:
            db_error(f.__name__, e, "Are you trying to reference an id that doesn't exist?")
            return None
        except sqlite3.NotSupportedError as e:
            db_error(f.__name__, e, "One feature isn't supported by your local database.")
            return None
        except sqlite3.ProgrammingError as e:
            db_error(f.__name__, e, "The query was invalid.")
            return None
        except sqlite3.DatabaseError as e:
            db_error(f.__name__, e)
            return None
    return decorated


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
        :PRE: _
        :POST: The database object will have a connection to the database file and the tables will be set up.
        """
        self.connect()
        if not self.validate_tables():
            self.commit()
        return self

    def __exit__(self, *args):
        """Closes the connection to the database file.

        :author: Mathieu
        :PRE: The connection to the database needs to exist.
        :POST: The connection is broken.
        """
        self.disconnect()

    def connect(self):
        """Starts the connection to the database file with the path stored.

        :author: Carlos
        :PRE: _
        :POST: Creates a new connection to the database file.
        """
        if self._connection:
            self.disconnect()
        self._connection = sqlite3.connect(self._path)
        self._connection.row_factory = sqlite3.Row

    def disconnect(self):
        """Closes the connection to the database file.

        :author: Mathieu
        :PRE: The connection to the database needs to exist.
        :POST: Closes the connection to the database file.
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
        :PRE: The connection to the database needs to exist.
        :POST: Executes the sql query and returns a database cursor.
        """
        return self._connection.execute(query, parameters)

    def commit(self):
        """Commits a database transaction.

        :author: Mathieu
        :PRE: The connection to the database needs to exist.
        :POST: The changes made are commited.
        """
        self._connection.commit()

    @db_query
    def validate_tables(self):
        """Checks if the expected tables exist in the database and creates them if they don't.

        :author: Carlos
        :PRE: The connection to the database needs to exist.
        :POST: Returns False if any table had to be created, True otherwise.
        """
        tables = (
            "groups",
            "songs",
            "songFeaturing",
            "playlists",
            "playlistSongs",
            "albums",
            "albumSongs",
            "settings"
        )

        output = True

        if not self.foreign_keys():
            self.execute(db_queries.foreign_keys_enable)

        for table in tables:
            if not self.table_exists(table):
                self.execute(getattr(db_queries, f"create_{table}"))
                output = False

        return output

    @db_query
    def table_exists(self, name: str) -> int:
        """Checks if a table exist in the database.

        :param name: name of the table to check.
        :PRE: The connection to the database needs to exist.
        :POST: Returns 1 if it exists, 0 if it doesn't.
        """
        result = self.execute(db_queries.table_exists, (name,))
        return result.fetchone()[0]

    @db_query
    def foreign_keys(self) -> int:
        """Checks if foreign_keys are enabled in sqlite.

        :PRE: The connection to the database needs to exist.
        :POST: Returns 1 if enabled, 0 if disabled.
        """
        result = self.execute(db_queries.foreign_keys)
        return result.fetchone()[0]

    @db_query
    def count_songs(self, filters: dict = None):
        """Returns the amount of songs, after being filtered.

        :param filters: Filters the songs need to fit to be counted.
        :PRE: The connection to the database needs to exist.
        :POST: The amount of songs.
        """
        default = {
            "genre": None,
            "name": None,
            "group": None
        }

        if filters:
            default = {**default, **filters}

        genre = (db_queries.append_genre, default["genre"])
        name = (db_queries.append_name, fuzy(default["name"]))
        group = (db_queries.append_group, fuzy(default["group"]))
        query, params = query_append(db_queries.count_songs, "", genre, name, group)

        return self.execute(query, params).fetchone()[0]

    @db_query
    def get_playlist(self, name: str = "", playlist_id: int = -1):
        """Obtains a playlist from the database based on its name/id.

        :param name: The name of the playlist.
        :param playlist_id: The id of the playlist.
        :PRE: The connection to the database needs to exist.
        :POST: Returns a Row if the playlist exists, None if it doesn't.
        """
        if playlist_id < 0:
            return self.execute(db_queries.get_playlist, (name,)).fetchone()
        else:
            return self.execute(db_queries.get_playlist_with_id, (playlist_id,)).fetchone()

    @db_query
    def get_playlists(self):
        """Obtains a list with all the playlists created.

        :PRE: The connection to the database needs to exist.
        :POST: Returns a list with Rows
        """
        return self.execute(db_queries.get_playlists).fetchall()

    @db_query
    def get_song(self, song_name: str = "", group_id: Optional[str] = None, song_id: int = -1):
        """Obtains a song from the database based on its name, and optionally its group name.

        :param song_name: The name of the song.
        :param group_id: The id of the group.
        :param song_id: The id of the song to fetch.
        :PRE: The connection to the database needs to exist.
        :POST: Returns a list of Rows if the song(s) exist, None if it doesn't,
               returns only one Row if the group is provided.
        """
        if not group_id and song_id < 0:
            songs = list(map(dict, self.execute(db_queries.get_song, (song_name,)).fetchall()))

            for song in songs:
                song["featuring"] = self.get_song_featuring(song["song_id"])
            return songs
        else:
            if song_id < 0:
                song = self.execute(db_queries.get_song_with_group, (song_name, group_id)).fetchone()
            else:
                song = self.execute(db_queries.get_song_with_id, (song_id,)).fetchone()
            if song:
                song = dict(song)
                song["featuring"] = self.get_song_featuring(song["song_id"])
            return song

    @db_query
    def get_song_featuring(self, song_id: int):
        """Obtains the groups featured in a song.

        :param song_id: The id of the song.
        :PRE: The connection to the database needs to exist.
        :POST: Returns a list of Rows with the groups featured in the song.
        """
        return self.execute(db_queries.get_song_featuring, (song_id,)).fetchall()

    @db_query
    def get_songs(self, filters: dict = None, offset: int = 0, limit: int = 50):
        """Obtains a defined amount of songs, after being filtered.

        :param filters: The filters the songs need to fit.
        :param offset: The offset in the database query.
        :param limit: The lmimit in the database query.
        :PRE: The connection to the database needs to exist.
        :POST: Returns an array of Rows of the songs.
        """
        default = {
            "genre": None,
            "name": None,
            "group": None,
            "group_id": None
        }

        if filters:
            default = {**default, **filters}

        genre = (db_queries.append_genre, default["genre"])
        name = (db_queries.append_name, fuzy(default["name"]))
        group = (db_queries.append_group, fuzy(default["group"]))
        group_id = (db_queries.append_group_id, default["group_id"])
        query, params = query_append(db_queries.get_songs, db_queries.paging, genre, name, group, group_id)

        songs = list(map(dict, self.execute(query, (*params, limit, offset)).fetchall()))

        for song in songs:
            song["featuring"] = self.get_song_featuring(song["song_id"])

        return songs

    @db_query
    def get_group(self, name: str = '', verbose: bool = False, group_id: int = -1):
        """Obtains a group from the database based on its name,
        will return even more info about it if requested.

        :param name: The name of the group.
        :param verbose: If more info should be provided.
        :param group_id: The group id instead of the name. Optional.
        :PRE: The connection to the database needs to exist.
        :POST: Returns Row if the group exists, None if it doesn't.
               If verbose the counts of songs and albums will also be provided.
        """
        if group_id >= 0:
            group_query = self.execute(db_queries.get_group_with_id, (group_id,)).fetchone()
        else:
            group_query = self.execute(db_queries.get_group, (name,)).fetchone()
        if not verbose:
            return group_query
        elif group_query:
            songs = self.execute(db_queries.count_group_songs, (group_query["group_id"],)).fetchone()["count"]
            albums = self.execute(db_queries.count_group_albums, (group_query["group_id"],)).fetchone()["count"]
            return group_query, songs, albums

    @db_query
    def get_album(self, name: str = "", group_id: Optional[int] = None, album_id: int = -1):
        """Obtains an album from the database based on its name.

        :param name: The name of the album.
        :param group_id: The id of the group, optional
        :param album_id: If an id needs to be
        :PRE: The connection to the database needs to exist.
        :POST: Returns a Row if the album exists and the group is provided, None if it doesn't.
               If no group is provided a list of Rows.
        """
        if album_id >= 0:
            return self.execute(db_queries.get_album_with_id, (album_id,)).fetchone()
        if group_id:
            return self.execute(db_queries.get_album_with_group, (name, group_id)).fetchone()
        else:
            return self.execute(db_queries.get_album, (name,)).fetchall()

    @db_query
    def get_album_songs(self, album_id: int):
        """Obtains a list with all the songs an album contains.

        :param album_id: The id of the album.
        :PRE: The connection to the database needs to exist.
        :POST: Returns a list of Rows with songs, if the album doesn't exist the list will be empty.
        """
        songs = list(map(dict, self.execute(db_queries.get_songs_album, (album_id,)).fetchall()))

        for song in songs:
            song["featuring"] = self.get_song_featuring(song["song_id"])

        return songs

    @db_query
    def add_song_playlist(self, playlist_id: int, song_id: int):
        """Adds an existing song to an existing playlist.

        :param playlist_id: The id of the playlist.
        :param song_id: The id of the song.
        :PRE: The connection to the database needs to exist, the song and playlist need to exist in the database.
        :POST: The song will be linked to playlist.
        """
        self.execute(db_queries.add_song_playlist, (playlist_id, song_id))

    @db_query
    def get_playlist_songs(self, playlist_id: int):
        """Returns the songs contained in a playlist.

        :param playlist_id: The id of the playlist.
        :PRE: The connection to the database needs to exist.
        :POST: Returns a list of Rows of the songs in the playlist,
               each song has a "featuring" field with Rows of the featured groups.
        """
        songs = list(map(dict, self.execute(db_queries.get_playlist_songs, (playlist_id,)).fetchall()))

        for song in songs:
            song["featuring"] = self.get_song_featuring(song["song_id"])

        return songs

    @db_query
    def create_playlist(self, name: str, author: str) -> int:
        """Creates a new playlist in the database.

        :param name: Name for the playlist.
        :param author: The user that created the playlist.
        :PRE: The connection to the database needs to exist.
        :POST: Returns the id of the created playlist
        """
        return self.execute(db_queries.create_playlist, (name, author)).lastrowid

    @db_query
    def create_group(self, name: str, members: List[str]) -> int:
        """Creates a new group in the database.

        :param name: Name of the group.
        :param members: List of members of the group.
        :PRE: The connection to the database needs to exist.
        :POST: Returns the id of the created group.
        """
        return self.execute(db_queries.create_group, (name, ','.join(members))).lastrowid

    @db_query
    def update_group(self, group_id: int, members: List[str]):
        """Updates the information stored for a group in the database.

        :param group_id: The id of group to update.
        :param members: The members of the group.
        :PRE: The connection to the database needs to exist, the group needs to exist in the database.
        :POST: The group is updated with the provided info.
        """
        self.execute(db_queries.update_group, (','.join(members), group_id))

    @db_query
    def create_song(self, name: str, link: str, genre: str,
                    duration: Optional[int], group_id: int, featuring: List[int]) -> int:
        """Creates a new song in the database.

        :param name: Name of the song.
        :param link: Link to the song in YouTube.
        :param genre: Genre of the song.
        :param duration: Duration of the song. Optional.
        :param group_id: Id of the author of the song.
        :param featuring: List of id's for the groups featured in this song.
        :PRE: The connection to the database needs to exist,
              the main and featuring groups needs to exist in the database.
        :POST: Returns the id of the created song.
        """
        song_id = self.execute(db_queries.create_song, (name, link, genre, group_id, duration)).lastrowid

        for featuring_id in featuring:
            self.execute(db_queries.add_song_featuring, (song_id, featuring_id))

        return song_id

    @db_query
    def update_song(self, song_id: int, link: str, genre: str,
                    duration: int, featuring: Optional[List[int]] = None):
        """Updates the information stored for a song in the database.

        :param song_id: Id of the song to update.
        :param link: Link to the song in YouTube.
        :param genre: Genre of the song.
        :param duration: Duration of the song.
        :param featuring: List of id's for the groups featuring this song. Optional.
        :PRE: The connection to the database needs to exist,
              the song and featuring groups needs to exist in the database.
        :POST: The song is updated with the data provided.
        """
        self.execute(db_queries.update_song, (link, genre, duration, song_id))

        if featuring is not None:
            self.execute(db_queries.delete_song_featuring, (song_id,))
            for featuring_id in featuring:
                self.execute(db_queries.add_song_featuring, (song_id, featuring_id))

    @db_query
    def create_album(self, name: str, songs: List[int], group_id: int) -> int:
        """Creates a new album in the database.

        :param name: Name of the album.
        :param songs: List of id's for the songs included in the album.
        :param group_id: Id of the author of the album.
        :PRE: The connection to the database needs to exist, the group and songs needs exist in the database.
        :POST: Returns the id of the album created.
        """
        album_id = self.execute(db_queries.create_album, (name, group_id)).lastrowid
        for song_id in songs:
            self.execute(db_queries.add_song_album, (album_id, song_id))
        return album_id

    @db_query
    def update_album(self, album_id: int, songs: List[int]):
        """Updates the information stored for an album in the database.

        :param album_id: Id of the album to update.
        :param songs: List of id's for the songs included in the album.
        :PRE: The connection to the database needs to exist, the album and songs need to exist in the database.
        :POST: The album is updated with the data provided.
        """
        self.execute(db_queries.delete_album_songs, (album_id,))
        for song_id in songs:
            self.execute(db_queries.add_song_album, (album_id, song_id))

    @db_query
    def get_setting(self, key: str, default: str = None) -> str:
        """Returns a stored setting value if it has been saved.

        :param key: The key to find the value.
        :param default: The default value.
        :PRE: The connection to the database needs to exist.
        :POST: Returns the value if it's found, the default one otherwise.
        """
        row = self.execute(db_queries.get_setting, (key,)).fetchone()
        if row is None:
            return default

        return row["value"]

    @db_query
    def set_setting(self, key: str, value: str):
        """Stores a setting value in the database.

        :param key: The key to stored the value under.
        :param value: The value to store.
        :PRE: The connection to the database needs to exist.
        :POST: The setting is set or overriden.
        """
        self.execute(db_queries.set_setting, (key, str(value)))

    @db_query
    def get_albums(self):
        """Obtains a list with all the albums created.

        :PRE: The connection to the database needs to exist.
        :POST: Returns a list of Rows of the albums.
        """
        return self.execute(db_queries.get_albums).fetchall()

    @db_query
    def get_groups(self):
        """Obtains a list with all the groups created.

        :PRE: The connection to the database needs to exist.
        :POST: Returns a list of Rows of the groups.
        """
        return self.execute(db_queries.get_groups).fetchall()

    @db_query
    def get_genres(self):
        """Obtains a list with all the albums created.

        :PRE: The connection to the database needs to exist.
        :POST: Returns a list of genres stored in the database, formatted to have the first letter in caps.
        """
        genres = self.execute(db_queries.get_genres).fetchall()

        genres = [g["genre"] for g in genres]
        return [g[0].upper() + g[1:] for g in genres]
