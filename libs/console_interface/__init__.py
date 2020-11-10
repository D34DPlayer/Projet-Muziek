from ..database import DBMuziek
from argparse import Namespace


def cli_add(db: DBMuziek, arguments: Namespace):
    if arguments.TYPE == 'song':
        add_song(db)
    elif arguments.TYPE == 'album':
        add_album(db)
    else:
        add_group(db)


def cli_list(db: DBMuziek, arguments: Namespace):
    if arguments.TYPE == 'song':
        list_song(db, arguments.NAME)
    elif arguments.TYPE == 'album':
        list_album(db, arguments.NAME)
    else:
        list_group(db, arguments.NAME)


def cli_playlist(db: DBMuziek, arguments: Namespace):
    if arguments.song:
        add_song_playlist(db, arguments.NAME, arguments.song)
    else:
        list_playlist(db, arguments.NAME)


def add_song(db: DBMuziek):
    return True


def add_song_playlist(db: DBMuziek, name: str, songs: list[str]):
    playlist = db.execute('SELECT playlist_id, author FROM playlists WHERE name = ?', (name,)).fetchone()
    if playlist is None:
        print(f'The playlist "{name}" does not exists.')
        return

    playlist_id, author = playlist
    for song_name in songs:
        song = db.execute('SELECT song_id FROM songs WHERE name = ?', (song_name,)).fetchone()
        if song is None:
            print(f'The song "{song_name}" does not exists. Ignoring ...')
            continue

        db.execute('INSERT OR IGNORE INTO playlistSongs VALUES (?, ?)', (playlist_id, song[0]))
        print(f'The song "{song_name}" has been successfully added to the playlist "{name}".')

    db.commit()


def add_group(db: DBMuziek):
    return True


def add_album(db: DBMuziek):
    return True


def list_song(db: DBMuziek, name: str):
    return True


def list_group(db: DBMuziek, name: str):
    return True


def list_album(db: DBMuziek, name: str):
    return True


def list_playlist(db: DBMuziek, name: str):
    return True
