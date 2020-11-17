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

count_songs = "SELECT count(*) FROM songs;"

count_songs_genre = "SELECT count(*) FROM songs WHERE genre = ?;"

get_playlist = "SELECT playlist_id, author FROM playlists WHERE name = ?;"

get_song = "SELECT song_id FROM songs WHERE name = ?;"

get_songs = '''
SELECT s.song_id, s.name, s.duration, g.name
    FROM songs as s
        LEFT JOIN groups as g ON s.group_id = g.group_id
    WHERE genre = ?
    LIMIT ? OFFSET ?;
'''

get_group = "SELECT group_id FROM groups WHERE name = ?;"

add_song_playlist = "INSERT OR IGNORE INTO playlistSongs VALUES (?, ?);"

get_playlist_data = '''
SELECT s.name, s.duration, g.name
    FROM playlistSongs as p
        LEFT JOIN songs AS s ON s.song_id = p.song_id
        LEFT JOIN groups AS g ON g.group_id = s.group_id
    WHERE p.playlist_id = ?;
'''

create_playlist = "INSERT INTO playlists(name, author) VALUES (?, ?);"

create_group = "INSERT INTO groups(name, members) VALUES (?, ?);"

update_group = "UPDATE groups SET members = ? where group_id = ?;"

create_song = "INSERT INTO songs(name, link, genre, group_id) VALUES (?, ?, ?, ?);"

update_song = "UPDATE songs SET link = ?, genre = ?, group_id = ? where song_id = ?;"

search_song = "SELECT song_id, name FROM songs WHERE name LIKE ?;"

get_album = "SELECT album_id, group_id FROM albums WHERE name = ?;"

create_album = "INSERT INTO albums(name, group_id) VALUES (?, ?);"

add_song_album = "INSERT OR IGNORE INTO albumSongs VALUES (?, ?);"

delete_album_songs = "DELETE FROM albumSongs WHERE album_id = ?;"

