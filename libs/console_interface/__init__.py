from typing import List
import logging

from ..database import DBMuziek
from ..downloader import SongDownloader
from . import utils


handler = logging.FileHandler("muziek.log", "a", encoding="utf-8")
formatter = logging.Formatter('[Muziek] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger("cli")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.info("Muziek has been launched.")


def add_song(db: DBMuziek, name: str = None, group_id: int = None):
    """Add a song to the database and ask the user for the needed info.
        There's also the option to modify a song that already exists in the database,
        and to create the group if it doesn't exist yet.

        :author: Carlos
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
            return song["song_id"]

    link = utils.question("Youtube link")

    genre = utils.question("Genre")

    if not group_id:
        group = utils.question("Group")

        if not (group_query := db.get_group(group)):
            reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'n' or not (group_id := add_group(db, group)):
                return None
        else:
            group_id = group_query["group_id"]

    with db.connection:
        if update == 'y':
            db.update_song(song["song_id"], link, genre, group_id)
            song_id = song["song_id"]
            logger.info(f"The song {name} has been updated.")
        else:
            song_id = db.create_song(name, link, genre, group_id)
            logger.info(f"The song {name} has been added with the ID {song_id}.")

    return song_id


def add_song_playlist(db: DBMuziek, name: str, songs: List[str]):
    playlist = db.get_playlist(name)
    if playlist is None:
        with db.connection:
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
            song_id = song["song_id"]

        with db.connection:
            db.add_song_playlist(playlist_id, song_id)
            print(f'The song "{song_name}" has been successfully added to the playlist "{name}".')
            logger.info(f'The song "{song_name}" has been successfully added to the playlist "{name}".')


def add_group(db: DBMuziek, name: str = None):
    """Add a group to the database and ask the user for the needed info.
    There's also the option to modify a group that already exists in the database.

    :author: Carlos
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
            return group["group_id"]

    members = []
    while True:
        if not len(members):
            member = utils.question("Member 1")
        else:
            member = utils.question(f"Member {len(members) + 1} ('Done' if there aren't any more)")
            if member == "Done":
                break
        members.append(member)

    with db.connection:
        if update == 'y':
            db.update_group(group["group_id"], members)
            group_id = group["group_id"]
            logger.info(f"The group {name} has been updated.")
        else:
            group_id = db.create_group(name, members)
            logger.info(f"The group {name} has been added with the ID {group_id}.")

    return group_id


def add_album(db: DBMuziek):
    """Add an album to the database and ask the user for the needed info.
        There's also the option to modify an album that already exists in the database,
        and to create the group and songs if they don't exist yet.

        :author: Carlos
        :param db: The used database.
        :return: The id of the created/modified album. None if nothing was created.
    """
    name = utils.question("Name")

    update = 'n'
    if album := db.get_album(name):
        update = utils.question_choice(f'The album "{name}" already exists. Do you want to update it?', ['y', 'n'])
        if update == 'n':
            return album["album_id"]
        else:
            group_id = album["group_id"]
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
            song_id = song_query["song_id"]
        songs.append(song_id)

    with db.connection:
        if update == 'y':
            db.update_album(album["album_id"], songs)
            album_id = album["album_id"]
            logger.info(f"The album {name} has been updated.")
        else:
            album_id = db.create_album(name, songs, group_id)
            logger.info(f"The group {name} has been added with the ID {album_id}.")

    return album_id


def list_songs(db: DBMuziek, filters: dict):
    """List all songs from the database and display it on the screen with pagination.

        :author: Mathieu
        :param db: The used database.
        :param filters: The filters to apply before listing.
    """
    # Make pages of 20 songs
    pages, rem = divmod(db.count_songs(filters), 20)
    pages += rem > 0 # then add the last page if there are remaining songs

    page = 0
    while page > -1:
        songs = db.get_songs(filters, offset=page * 20, limit=20)
        utils.display_songs(songs)
        page = utils.pagination(pages, page + 1) - 1


def list_group(db: DBMuziek, name: str):
    return True


def list_album(db: DBMuziek, name: str):
    return True


def list_playlist(db: DBMuziek, name: str):
    """Show the content of a playlist and create it if it doesn't exist yet.

    :author: Mathieu
    :param db: The database used.
    :param name: The playlist's name.
    """
    playlist = db.get_playlist(name)
    if playlist is None:
        with db.connection:
            playlist = create_playlist(db, name)
            print(f'The playlist "{name}" has been successfully created.')
            logger.info(f'The playlist "{name}" has been successfully created.')

    playlist_id, author = playlist
    utils.print_underline(f'Playlist "{name}" by [{author}] :', style='=')

    songs = db.get_playlist_data(playlist_id)
    utils.display_songs(songs)


def create_playlist(db: DBMuziek, name: str) -> (int, str):
    """Create a playlist in the database and return its id and author.
        Does not commit the transaction.

    :author: Mathieu
    :param db: The database used.
    :param name: The playlist's name.
    :return: The playlist's id and its author.
    """
    author = utils.getuser()

    playlist_id = db.create_playlist(name, author)

    return playlist_id, author


def download_song(db: DBMuziek, name: str):
    downloader = SongDownloader(logger)

    if not (song_query := db.get_song(name)):
        reply = utils.question_choice(f'The song "{name}" doesn\'t. exist yet. Do you want to create it?',
                                      ['y', 'n'])
        if reply == 'y':
            return add_song(db, name)
        else:
            return None

    print('Checking if the link is valid...')

    if not (video_info := downloader.fetch_song(song_query["link"])):
        print("No video could be found with the provided link. Modify the song entry to change it.")
        return None

    print('Checking if the song has already been downloaded...')

    if downloader.is_downloaded(song_query["song_id"]):
        reply = utils.question_choice(f'The song {name} has already been downloaded. Do you want to override it?',
                                      ['y', 'n'])
        if reply == "n":
            return
        else:
            downloader.delete_song(song_query["song_id"])

    print(f'The video called {video_info["title"]} is being downloaded...')

    downloader.download_song(song_query)

    print("Download complete.")
    logger.info(f'The song {name} has been downloaded.')
