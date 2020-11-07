table_exists = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?;"

foreign_keys = "PRAGMA foreign_keys;"

foreign_keys_enable = "PRAGMA foreign_keys = ON;"

groups = '''
CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    members TEXT NOT NULL 
)
'''

songs = '''
CREATE TABLE songs (
    song_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    link TEXT NOT NULL,
    genre TEXT NOT NULL,
    duration NUMERIC,
    dateRelease INTEGER,
    FOREIGN KEY (group_id) REFERENCES GROUPS (group_id)
)
'''

albums = '''
CREATE TABLE albums (
    album_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    dateRelease INTEGER,
    FOREIGN KEY (group_id) REFERENCES GROUPS (group_id)
)
'''

albumSongs = '''
CREATE TABLE albumSongs (
    album_id INTEGER,
    song_id INTEGER,
    PRIMARY KEY (album_id, song_id),
    FOREIGN KEY (song_id) REFERENCES SONGS (song_id),
    FOREIGN KEY (album_id) REFERENCES ALBUMS (album_id)
)
'''

playlists = '''
CREATE TABLE playlists (
    playlist_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    author TEXT NOT NULL
)
'''

playlistSongs = '''
CREATE TABLE playlistSongs (
    playlist_id INTEGER,
    song_id INTEGER,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (song_id) REFERENCES SONGS (song_id),
    FOREIGN KEY (playlist_id) REFERENCES PLAYLISTS (playlist_id)
)
'''