from typing import List
import logging

from ..database import DBMuziek
from ..downloader import SongDownloader
from ..youtube_api import YoutubeAPI
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
        :param db: The database used.
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

    link = ""
    downloader = SongDownloader(logger)
    while not link:
        link = utils.question("Youtube link")
        if not (downloader.fetch_song(link)):
            print("No video could be found with the provided link.")
            link = ""

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

    featuring = []
    while True:
        reply = utils.question(f"Featuring {len(featuring) + 1} ('Done' if there aren't any more)")
        if reply == "Done":
            break
        if not (group_query := db.get_group(reply)):
            reply2 = utils.question_choice(f'The group "{reply}" doesn\'t. exist yet. Do you want to create it?',
                                           ['y', 'n'])
            if reply2 == 'n' or not (featuring_id := add_group(db, reply)):
                continue
        else:
            featuring_id = group_query["group_id"]

        featuring.append(featuring_id)

    with db.connection:
        if update == 'y':
            db.update_song(song["song_id"], link, genre, group_id, featuring)
            song_id = song["song_id"]
            logger.info(f"The song {name} has been updated.")
        else:
            song_id = db.create_song(name, link, genre, group_id, featuring)
            logger.info(f"The song {name} has been added with the ID {song_id}.")

    download = utils.question_choice("Do you want to download the song?", ['y', 'n'])
    if download == 'y':
        downloader.download_song(db.get_song(name))
        print("Download complete.")
        logger.info(f"The song {name} has been downloaded.")
    return song_id


def add_song_playlist(db: DBMuziek, name: str, songs: List[str]):
    """Add a list of songs to a playlist, will create the playlist if needed.
    If a song doesn't exist yet, the user can create it diretly if they want to.

    :author: Mathieu
    :param db: The database used.
    :param name: The name of the playlist.
    :param songs: List of names of songs to add to the playlist.
    """
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
    :param db: The database used.
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


def add_album(db: DBMuziek, name: str = None):
    """Add an album to the database and ask the user for the needed info.
        There's also the option to modify an album that already exists in the database,
        and to create the group and songs if they don't exist yet.

    :author: Carlos
    :param db: The database used.
    :param name: The name of the album.
    :return: The id of the created/modified album. None if nothing was created.
    """
    if not name:
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
        :param db: The database used.
        :param filters: The filters to apply before listing.
    """
    # Make pages of 20 songs
    pages, rem = divmod(db.count_songs(filters), 20)
    pages += rem > 0  # then add the last page if there are remaining songs

    page = 0
    while page > -1:
        songs = db.get_songs(filters, offset=page * 20, limit=20)
        utils.display_songs(songs)
        page = utils.pagination(pages, page + 1) - 1


def list_group(db: DBMuziek, name: str):
    """List the information about a group stored in the database.

    :author: Carlos
    :param db: The database used.
    :param name: The name of the group.
    """
    if not (group_query := db.get_group(name, True)):
        reply = utils.question_choice(f'The group "{name}" doesn\'t. exist yet. Do you want to create it?',
                                      ['y', 'n'])
        if reply == 'y':
            return add_group(db, name)
        else:
            return None

    utils.print_underline('Group information:', style='=')

    print(f'''    Name: {name}
    Members: {', '.join(group_query[0]['members'].split(","))}
    Songs: {group_query[1]}
    Albums: {group_query[2]}
    ''')


def list_album(db: DBMuziek, name: str):
    """List the information about an album stored in the database, and a list of the songs it includes.

    :author: Carlos
    :param db: The database used.
    :param name: The name of the album.
    """
    if not (album_query := db.get_album(name, True)):
        reply = utils.question_choice(f'The album "{name}" doesn\'t. exist yet. Do you want to create it?',
                                      ['y', 'n'])
        if reply == 'y':
            return add_album(db, name)
        else:
            return None

    utils.print_underline('Album information:', style='=')

    print(f'''    Name: {name}
    Group: {album_query[0]["group_name"]}
    ''')

    utils.print_underline('Songs:', style='=')
    utils.display_songs(album_query[1])


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

    songs = db.get_playlist_songs(playlist_id)
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
    """Downloads the song requested based on the url stored in the database.

    :author: Carlos
    :param db: The database used.
    :param name: Name of the song to download.
    """
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
            return None
        else:
            downloader.delete_song(song_query["song_id"])

    print(f'The video called {video_info["title"]} is being downloaded...')

    downloader.download_song(song_query)

    print("Download complete.")
    logger.info(f'The song {name} has been downloaded.')


def list_yt_playlist(db: DBMuziek, name: str = None):
    """Lists your Youtube playlists.

    :author: Mathieu
    :param db: The database used.
    :param name: If not None, will list all songs from that playlist.
    """
    yt = YoutubeAPI(db)
    for playlist in yt.playlists:
        if name is None or playlist.title == name:
            print(playlist)

            if name is not None:
                for song in playlist.songs:
                    print(f'\t- {song}')

                break
    else:
        if name is not None:
            print(f'The playlist "{name}" does not exists.')


def import_from_yt(db: DBMuziek, name: str):
    """Imports a playlist from Youtube.

    :author: Mathieu
    :param db: The database used.
    """
    if db.get_playlist(name) is not None:
        print(f'The playlist "{name}" already exists.')
        return

    yt = YoutubeAPI(db)
    for playlist in yt.playlists:
        if playlist.title.lower() == name.lower():
            break
    else:
        print(f'Cannot find the playlist "{name}" on your Youtube account.')
        return

    playlist_id = create_playlist(db, name)[0]
    for song in playlist.songs:
        author, title = utils.strip_brackets(song.title).split('-')
        author, title = author.strip(), title.strip()

        print(f'Author: {author}')
        if utils.question_choice("Would you like to rename the song's author ?", 'yn') == 'y':
            author = input('Author: ').strip()

        if group_id := db.get_group(author) is None:
            group_id = db.create_group(author, [author])

        print(f'Title: {title}')
        if utils.question_choice("Would you like to rename the song's title ?", 'yn') == 'y':
            title = input('Title: ').strip()

        if song_id := db.get_song(title) is None:
            genre = utils.question("Song's genre: ")
            song_id = db.create_song(title, song.url, genre, group_id, [])

        db.add_song_playlist(playlist_id, song_id)
