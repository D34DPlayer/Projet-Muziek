from typing import List, Optional
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


def add_song(db: DBMuziek, name: Optional[str] = None, group_id: Optional[int] = None):
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

    if not group_id:
        group = utils.question("Group")

        if not (group_query := db.get_group(group)):
            reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'n' or not (group_id := add_group(db, group)):
                return None
        else:
            group_id = group_query["group_id"]

    update = 'n'
    if song := db.get_song(name, group_id):
        update = utils.question_choice(f'The song "{name}" already exists. Do you want to update it?', ['y', 'n'])
        if update == 'n':
            return song["song_id"]

    link = ""
    downloader = SongDownloader(logger)
    while not link:
        link = utils.question("Youtube link", song["link"] if song else None)
        if not (downloader.fetch_song(link)):
            print("No video could be found with the provided link.")
            link = ""

    genre = utils.question("Genre", song["genre"] if song else None)

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
            db.update_song(song["song_id"], link, genre, downloader['duration'], featuring)
            song_id = song["song_id"]
            logger.info(f"The song {name} has been updated.")

            if downloader.is_downloaded(song_id):
                download = utils.question_choice("Do you want to redownload the song?", ['y', 'n'])
                if download == 'n':
                    downloader.update_metadata(db.get_song(name, group_id))
                    logger.info(f"The metadata of the local song {name} has been updated.")
            else:
                download = utils.question_choice("Do you want to download the song?", ['y', 'n'])

        else:
            song_id = db.create_song(name, link, genre, downloader['duration'], group_id, featuring)
            logger.info(f"The song {name} has been added with the ID {song_id}.")
            download = utils.question_choice("Do you want to download the song?", ['y', 'n'])

    if download == 'y':
        downloader.download_song(db.get_song(name, group_id))
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

    playlist_id, author, playlist_name = playlist
    for song_name in songs:
        if not (song := utils.choose_song(db.get_song(song_name))):
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


def add_group(db: DBMuziek, name: Optional[str] = None):
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


def add_album(db: DBMuziek, name: Optional[str] = None):
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

    group = utils.question("Group")

    update = 'n'
    if not (group_query := db.get_group(group)):
        reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?',
                                      ['y', 'n'])
        if reply == 'n' or not (group_id := add_group(db, group)):
            return None
    else:
        group_id = group_query[0]

    if album := db.get_album(name, group_id):
        update = utils.question_choice(f'The album "{name}" already exists. Do you want to update it?', ['y', 'n'])
        if update == 'n':
            return album["album_id"]

    songs = []
    while True:
        if not len(songs):
            song = utils.question("Song 1")
        else:
            song = utils.question(f"Song {len(songs) + 1} ('Done' if there aren't any more)")
            if song == "Done":
                break
        if not (song_query := db.get_song(song, group_id)):
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
    if not (album_query := utils.choose_album(db.get_album(name))):
        reply = utils.question_choice(f'The album "{name}" doesn\'t. exist yet. Do you want to create it?',
                                      ['y', 'n'])
        if reply == 'y':
            return add_album(db, name)
        else:
            return None

    album_songs = db.get_album_songs(album_query["album_id"])

    utils.print_underline('Album information:', style='=')

    print(f'''    Name: {name}
    Group: {album_query["group_name"]}
    ''')

    utils.print_underline('Songs:', style='=')
    utils.display_songs(album_songs)


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

    playlist_id, author, playlist_name = playlist
    utils.print_underline(f'Playlist "{playlist_name}" by [{author}] :', style='=')

    songs = db.get_playlist_songs(playlist_id)
    utils.display_songs(songs)


def create_playlist(db: DBMuziek, name: str, author: Optional[str] = None) -> (int, str):
    """Create a playlist in the database and return its id and author.
        Does not commit the transaction.

    :author: Mathieu
    :param db: The database used.
    :param name: The playlist's name.
    :param author: The author, optional.
    :return: The playlist's id and its author.
    """
    if not author:
        author = utils.getuser()

    playlist_id = db.create_playlist(name, author)

    return playlist_id, author, name


def list_playlists(db: DBMuziek):
    playlists = db.get_playlists()

    print(f"You have {len(playlists)} playlists:")

    for playlist in playlists:
        print(f" \"{playlist['playlist_name']}\" created by {playlist['author']}")


def download_song(db: DBMuziek, name: str):
    """Downloads the song requested based on the url stored in the database.

    :author: Carlos
    :param db: The database used.
    :param name: Name of the song to download.
    """
    downloader = SongDownloader(logger)

    if not (song_query := utils.choose_song(db.get_song(name))):
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


def import_playlist(db: DBMuziek, name: str):
    if db.get_playlist(name):
        print(f"The playlist {name} already exists.")
        return

    buffer = utils.question("Playlist export code")

    buffer = utils.decode(buffer)

    with db.connection:
        for group in buffer["groups"]:
            if not db.get_group(group["name"]):
                db.create_group(group["name"], group["members"])

        songs = []

        for song in buffer["songs"]:
            group_query = db.get_group(song["group_name"])
            if not (song_query := db.get_song(song["song_name"], group_query["group_id"])):
                featuring = [db.get_group(n) for n in song["featuring"]]
                song_id = db.create_song(song["song_name"], song["link"], song["genre"],
                                         song["duration"], group_query["group_id"], featuring)
            else:
                song_id = song_query["song_id"]
            songs.append(song_id)

        playlist_id, *other = create_playlist(db, name, buffer["playlist"]["author"])

        for song_id in songs:
            db.add_song_playlist(playlist_id, song_id)

    print(f"The playlist {name} has been successfully imported.")
    logger.info(f"The playlist {name} has been successfully imported.")


def export_playlist(db: DBMuziek, name: str):
    buffer = {
        "groups": [],
        "songs": [],
        "playlist": {}
    }

    groups = []

    if not (playlist_query := db.get_playlist(name)):
        print(f"The playlist {name} doesn't exist yet, create it and add songs to it.")
        return None

    playlist_songs = db.get_playlist_songs(playlist_query['playlist_id'])

    if len(playlist_songs) == 0:
        print(f"The playlist {name} is empty, nothing will be exported.")
        return None

    for song in playlist_songs:
        if song["group_id"] not in groups:
            groups.append(song["group_id"])

            group = db.get_group(song["group_name"])
            buffer["groups"].append({
                "name": group["group_name"],
                "members": group["members"].split(",")
            })

        featured_groups = db.get_song_featuring(song["song_id"])

        for featured_group in featured_groups:
            if featured_group["group_id"] not in groups:
                groups.append(featured_group["group_id"])

                group = db.get_group(featured_group["group_name"])
                buffer["groups"].append({
                    "name": group["group_name"],
                    "members": group["members"].split(",")
                })

        buffer["songs"].append({
            "group_name": song["group_name"],
            "song_name": song["song_name"],
            "link": song["link"],
            "genre": song["genre"],
            "duration": song["duration"],
            "featuring": [f["group_name"] for f in featured_groups]
        })

    buffer["playlist"] = {
        "author": playlist_query["author"]
    }

    buffer = utils.encode(buffer)

    print(f"Share this text to share the playlist:\n {buffer}")
    logger.info(f"The playlist {name} has been successfully exported.")
