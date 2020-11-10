import math

from ..database import DBMuziek
from . import utils
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
    playlist = db.execute('SELECT playlist_id, author FROM playlists WHERE name = ?', (name,)).fetchone()
    if playlist is None:
        print(f'The playlist "{name}" does not exists.')
        return

    playlist_id, author = playlist
    utils.print_underline(f'Playlist "{name}" by [{author}] :', style='=')

    songs = db.execute('''
        SELECT s.name, s.duration, g.name
        FROM playlistSongs as p
        LEFT JOIN songs AS s ON s.song_id = p.song_id
        LEFT JOIN groups AS g ON g.group_id = s.group_id
        WHERE p.playlist_id = ?
    ''', (playlist_id,)).fetchall()

    if len(songs) == 0:
        print('<empty>')
        return

    length = math.ceil(math.log10(len(songs)))
    for i, (song, duration, group) in enumerate(songs, 1):
        if duration is None:
            duration = '??:??'
        else:
            duration = '{}:{}'.format(*divmod(duration, 60))

        print(f'{i:>{length}}. ({duration}) {song} - {group}')
