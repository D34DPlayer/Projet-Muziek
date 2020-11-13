import math
from typing import List

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


def add_song(db: DBMuziek, name: str = None):
    if not name:
        name = utils.question("Name")

    update = 'n'
    if song := db.get_song(name):
        update = utils.question_choice(f'The song "{name}" already exists. Do you want to update it?', ['y', 'n'])

    link = utils.question("Youtube link")

    genre = utils.question("Genre")

    group = utils.question("Group")

    if not (group_query := db.get_group(group)):
        reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?', ['y', 'n'])
        if reply == 'n':
            return None
        else:
            group_id = add_group(db, group)
    else:
        group_id = group_query[0]

    if update == 'y':
        db.update_song(song[0], link, genre, group_id)
        song_id = song[0]
    else:
        song_id = db.create_song(name, link, genre, group_id)
    db.commit()

    return song_id


def add_song_playlist(db: DBMuziek, name: str, songs: List[str]):
    playlist = db.get_playlist(name)
    if playlist is None:
        playlist = create_playlist(db, name)
        print(f'The playlist "{name}" has been successfully created.')

    playlist_id, author = playlist
    for song_name in songs:
        song = db.get_song(song_name)
        if song is None:
            reply = utils.question_choice(f'The song "{song_name}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'n':
                continue
            else:
                if not (song_id := add_song(db, song_name)):
                    continue
        else:
            song_id = song[0]

        db.add_song_playlist(playlist_id, song_id)
        print(f'The song "{song_name}" has been successfully added to the playlist "{name}".')

    db.commit()


def add_group(db: DBMuziek, name: str = None):
    if not name:
        name = utils.question("Name")

    update = 'n'
    if group := db.get_group(name):
        update = utils.question_choice(f'The group "{name}" already exists. Do you want to update it?', ['y', 'n'])

    members = []
    while True:
        if not len(members):
            member = utils.question(f"Member 1")
        else:
            member = utils.question(f"Member {len(members) + 1} ('Done' if there aren't any more)")
            if member == "Done":
                break
        members.append(member)

    if update == 'y':
        db.update_group(group[0], members)
        group_id = group[0]
    else:
        group_id = db.create_group(name, members)
    db.commit()

    return group_id


def add_album(db: DBMuziek):
    return True


def list_song(db: DBMuziek, name: str):
    return True


def list_group(db: DBMuziek, name: str):
    return True


def list_album(db: DBMuziek, name: str):
    return True


def list_playlist(db: DBMuziek, name: str):
    playlist = db.get_playlist(name)
    if playlist is None:
        playlist = create_playlist(db, name)
        print(f'The playlist "{name}" has been successfully created.')
        db.commit()

    playlist_id, author = playlist
    utils.print_underline(f'Playlist "{name}" by [{author}] :', style='=')

    songs = db.get_playlist_data(playlist_id)

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


def create_playlist(db: DBMuziek, name: str) -> (int, str):
    """Create a playlist in the database and return its id and author.
    Does not commit the transaction.

    :param db: The to insert the new playlist.
    :param name: The playlist's name.
    :return: The playlist's id and its author.
    """
    author = utils.getuser()

    playlist_id = db.create_playlist(name, author)

    return playlist_id, author
