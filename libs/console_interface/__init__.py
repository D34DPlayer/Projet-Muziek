from typing import List

from ..database import DBMuziek
from . import utils


def add_song(db: DBMuziek, name: str = None, group_id: int = None):
    """Add a song to the database and ask the user for the needed info.
        There's also the option to modify a song that already exists in the database,
        and to create the group if it doesn't exist yet.
        @CARLOS

        :param db: The used database.
        :param name: The name of the song.
        :param group_id: The name of the group who made the song.
        :return: The id of the created/modified group. None if nothing was created/modified.
    """
    if not name:
        name = utils.question("Name")

    update = 'n'
    if song := db.get_song(name):
        update = utils.question_choice(f'The song "{name}" already exists. Do you want to update it?', ['y', 'n'])
        if update == 'n':
            return song[0]

    link = utils.question("Youtube link")

    genre = utils.question("Genre")

    if not group_id:
        group = utils.question("Group")

        if not (group_query := db.get_group(group)):
            reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?', ['y', 'n'])
            if reply == 'n' or not (group_id := add_group(db, group)):
                return None
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
        if not (song := db.get_song(song_name)):
            reply = utils.question_choice(f'The song "{song_name}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'n' or not (song_id := add_song(db, song_name)):
                continue
        else:
            song_id = song[0]

        db.add_song_playlist(playlist_id, song_id)
        print(f'The song "{song_name}" has been successfully added to the playlist "{name}".')

    db.commit()


def add_group(db: DBMuziek, name: str = None):
    """Add a group to the database and ask the user for the needed info.
    There's also the option to modify a group that already exists in the database.
    @CARLOS

    :param db: The used database.
    :param name: The name of the group.
    :return: The id of the created/modified group. None if nothing was created/modified.
    """
    if not name:
        name = utils.question("Name")

    update = 'n'
    if group := db.get_group(name):
        update = utils.question_choice(f'The group "{name}" already exists. Do you want to update it?', ['y', 'n'])
        if update == 'n':
            return group[0]

    members = []
    while True:
        if not len(members):
            member = utils.question("Member 1")
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
    """Add an album to the database and ask the user for the needed info.
        There's also the option to modify an album that already exists in the database,
        and to create the group and songs if they don't exist yet.
        @CARLOS

        :param db: The used database.
        :return: The id of the created/modified album. None if nothing was created.
    """
    name = utils.question("Name")

    update = 'n'
    if album := db.get_album(name):
        update = utils.question_choice(f'The album "{name}" already exists. Do you want to update it?', ['y', 'n'])
        if update == 'n':
            return album[0]
        else:
            group_id = album[1]
    else:
        group = utils.question("Group")
        if not (group_query := db.get_group(group)):
            reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'n' or not (group_id := add_group(db, group)):
                return None
        else:
            group_id = group_query[0]

    songs = []
    while True:
        if not len(songs):
            song = utils.question("Song 1")
        else:
            song = utils.question(f"Song {len(songs) + 1} ('Done' if there aren't any more)")
            if song == "Done":
                break
        if not (song_query := db.get_song(song)):
            reply = utils.question_choice(f'The song "{song}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'n' or not (song_id := add_song(db, song, group_id)):
                continue
        else:
            song_id = song_query[0]
        songs.append(song_id)

    if update == 'y':
        db.update_album(album[0], songs)
        album_id = album[0]
    else:
        album_id = db.create_album(name, songs, group_id)
    db.commit()

    return album_id


def list_songs(db: DBMuziek, filters: dict, offset: int = 0):
    songs = db.get_songs(filters, offset=offset, limit=20)
    utils.display_songs(songs)

    count = db.count_songs(filters) // 20
    if count > 1:
        page = int(offset / 20)

        start = min(count + 1, 2) if count < 5 else count + 1
        pages = [str(i) for i in range(1, start)]

        if count > 5:
            pages.append('...')
            pages += [str(i) for i in range(count - 2, count + 1)]

        list_pages = (' ' + ' '.join(pages) + ' ').replace(f' {page + 1} ', f' [{page + 1}] ')
        print(f'Pages:{list_pages}')

        page = 0
        while page < 1 or page > count:
            page = input('Display another page: ').strip()

            if len(page) == 0:
                return

            page = int(page) if page.isdecimal() else 0

        list_songs(db, filters, offset=(page - 1) * 20)


def list_group(db: DBMuziek, name: str):
    return True


def list_album(db: DBMuziek, name: str):
    return True


def list_playlist(db: DBMuziek, name: str):
    """Show the content of a playlist and create it if it doesn't exist yet.
    @MATHIEU

    :param db: The database used.
    :param name: The playlist's name.
    """
    playlist = db.get_playlist(name)
    if playlist is None:
        playlist = create_playlist(db, name)
        print(f'The playlist "{name}" has been successfully created.')
        db.commit()

    playlist_id, author = playlist
    utils.print_underline(f'Playlist "{name}" by [{author}] :', style='=')

    songs = db.get_playlist_data(playlist_id)
    utils.display_songs(songs)


def create_playlist(db: DBMuziek, name: str) -> (int, str):
    """Create a playlist in the database and return its id and author.
    Does not commit the transaction.

    :param db: The database used.
    :param name: The playlist's name.
    :return: The playlist's id and its author.
    """
    author = utils.getuser()

    playlist_id = db.create_playlist(name, author)

    return playlist_id, author


def search_song(db: DBMuziek, name: str):
    songs = db.search_song(f'%{name.lower()}%')
    utils.print_underline(f'Results for "{name}":')
    utils.display_songs(songs)
