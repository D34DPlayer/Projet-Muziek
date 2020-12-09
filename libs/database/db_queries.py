table_exists = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?;"

foreign_keys = "PRAGMA foreign_keys;"

foreign_keys_enable = "PRAGMA foreign_keys = ON;"

create_groups = '''
CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    members TEXT NOT NULL
);
'''

create_songs = '''
CREATE TABLE songs (
    song_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    link TEXT NOT NULL,
    genre TEXT NOT NULL,
    duration NUMERIC,
    dateRelease INTEGER,
    FOREIGN KEY (group_id) REFERENCES GROUPS (group_id)
);
'''

create_albums = '''
CREATE TABLE albums (
    album_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    dateRelease INTEGER,
    FOREIGN KEY (group_id) REFERENCES GROUPS (group_id)
);
'''

create_albumSongs = '''
CREATE TABLE albumSongs (
    album_id INTEGER,
    song_id INTEGER,
    PRIMARY KEY (album_id, song_id),
    FOREIGN KEY (song_id) REFERENCES SONGS (song_id),
    FOREIGN KEY (album_id) REFERENCES ALBUMS (album_id)
);
'''

create_playlists = '''
CREATE TABLE playlists (
    playlist_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    author TEXT NOT NULL
);
'''

create_playlistSongs = '''
CREATE TABLE playlistSongs (
    playlist_id INTEGER,
    song_id INTEGER,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (song_id) REFERENCES SONGS (song_id),
    FOREIGN KEY (playlist_id) REFERENCES PLAYLISTS (playlist_id)
);
'''

create_songFeaturing = '''
CREATE TABLE songFeaturing (
    song_id INTEGER,
    group_id INTEGER,
    PRIMARY KEY (song_id, group_id),
    FOREIGN KEY (song_id) REFERENCES SONGS (song_id),
    FOREIGN KEY (group_id) REFERENCES GROUPS (group_id)
);
'''

create_settings = '''
CREATE TABLE settings (
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (key)
);
'''

count_songs = '''
SELECT count(song_id)
    FROM songs as s
        LEFT JOIN groups as g ON s.group_id = g.group_id
'''

get_playlist = "SELECT playlist_id, author, name as playlist_name FROM playlists WHERE lower(name) = lower(?);"

get_playlists = "SELECT playlist_id, author, name as playlist_name FROM playlists;"

get_song = '''
SELECT song_id, s.name as song_name, duration, g.name as group_name, link, genre
    FROM songs as s
        LEFT JOIN groups g on s.group_id = g.group_id
    WHERE lower(s.name) = lower(?);
'''

get_song_with_group = '''
SELECT song_id, s.name as song_name, duration, g.name as group_name, link, genre
    FROM songs as s
        LEFT JOIN groups g on s.group_id = g.group_id
    WHERE lower(s.name) = lower(?) and g.group_id = ?;
'''

get_songs = '''
SELECT song_id, s.name as song_name, duration, g.name as group_name, link, genre
    FROM songs as s
        LEFT JOIN groups as g ON s.group_id = g.group_id
'''

append_genre = "lower(genre) = lower(?)"

append_name = "lower(s.name) LIKE lower(?)"

append_group = "lower(g.name) LIKE lower(?)"

paging = "LIMIT ? OFFSET ?"

get_group = '''
SELECT group_id, members, name as group_name
    FROM groups
    WHERE lower(name) = lower(?);
'''

add_song_playlist = "INSERT OR IGNORE INTO playlistSongs VALUES (?, ?);"

get_playlist_songs = '''
SELECT p.song_id as song_id, s.name as song_name, duration, g.name as group_name, link, genre, g.group_id as group_id
    FROM playlistSongs as p
        LEFT JOIN songs AS s ON s.song_id = p.song_id
        LEFT JOIN groups AS g ON g.group_id = s.group_id
    WHERE p.playlist_id = ?;
'''

create_playlist = "INSERT INTO playlists(name, author) VALUES (?, ?);"

create_group = "INSERT INTO groups(name, members) VALUES (?, ?);"

update_group = "UPDATE groups SET members = ? where group_id = ?;"

create_song = "INSERT INTO songs(name, link, genre, group_id, duration) VALUES (?, ?, ?, ?, ?);"

update_song = "UPDATE songs SET link = ?, genre = ?, duration = ? where song_id = ?;"

get_album = '''
SELECT album_id, a.group_id as group_id, g.name as group_name, a.name as album_name
    FROM albums as a
        LEFT JOIN groups as g on a.group_id = g.group_id
    WHERE lower(a.name) = lower(?);
'''

get_album_with_group = '''
SELECT album_id, a.group_id as group_id, g.name as group_name, a.name as album_name
    FROM albums as a
        LEFT JOIN groups as g on a.group_id = g.group_id
    WHERE lower(a.name) = lower(?) and g.group_id = ?;
'''

create_album = "INSERT INTO albums(name, group_id) VALUES (?, ?);"

add_song_album = "INSERT OR IGNORE INTO albumSongs VALUES (?, ?);"

delete_album_songs = "DELETE FROM albumSongs WHERE album_id = ?;"

add_song_featuring = "INSERT OR IGNORE INTO songFeaturing VALUES (?, ?);"

count_group_songs = "SELECT COUNT(song_id) as count FROM songs WHERE group_id = ?;"

count_group_albums = "SELECT COUNT(album_id) as count FROM albums WHERE group_id = ?;"

get_songs_album = '''
SELECT a.song_id as song_id, s.name as song_name, duration, g.name as group_name, link, genre
    FROM albumSongs as a
        LEFT JOIN songs as s on a.song_id = s.song_id
        LEFT JOIN groups as g on s.group_id = g.group_id
    WHERE a.album_id = ?;
'''

get_setting = "SELECT value FROM settings WHERE key = ?;"

set_setting = "INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?);"

delete_song_featuring = "DELETE FROM songFeaturing WHERE song_id = ?;"

get_song_featuring = """
SELECT f.group_id as group_id, g.name as group_name, members
    FROM songFeaturing as f
        LEFT JOIN groups as g on f.group_id = g.group_id
    WHERE f.song_id = ?;
"""
