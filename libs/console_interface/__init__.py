from typing import List, Optional

from ..logger import get_logger
from ..database import DBMuziek
from ..downloader import SongDownloader
from ..youtube_api import YoutubeAPI
from . import utils

logger = get_logger("cli")


def add_song(db: DBMuziek, name: Optional[str] = None, group_id: Optional[int] = None):
    """Add a song to the database and ask the user for the needed info.
        There's also the option to modify a song that already exists in the database,
        and to create the group if it doesn't exist yet.

    :author: Carlos
    :param db: The database used.
    :param name: The name of the song. Optional.
    :param group_id: The name of the group who made the song. Optional.
    :PRE: The database object needs to be connected.
    :POST: Asks the user of the relevant info and creates/modifies a song.
           Returns the id of the created/modified song. None if nothing was created/modified.
    """
    if not name:
        name = utils.question("Name")

    if not group_id:
        group = utils.question("Group")

        group_query = db.get_group(group)
        if not group_query:
            reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'y':
                group_id = add_group(db, group)
                if group_id is None:
                    return None
            else:
                return None
        else:
            group_id = group_query["group_id"]

    update = 'n'
    song = db.get_song(name, group_id)
    if song:
        update = utils.question_choice(f'The song "{name}" already exists. Do you want to update it?', ['y', 'n'])
        if update == 'n':
            return song["song_id"]

    link = ""
    downloader = SongDownloader()
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
        group_query = db.get_group(reply)
        if not group_query:
            reply2 = utils.question_choice(f'The group "{reply}" doesn\'t. exist yet. Do you want to create it?',
                                           ['y', 'n'])
            if reply2 == 'y':
                featuring_id = add_group(db, reply)
                if featuring_id is None:
                    continue
            else:
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
    :PRE: The database object needs to be connected.
    :POST: The playlist will be created if it doesn't exist and the songs will be added to it.
    """
    playlist = db.get_playlist(name)
    if playlist is None:
        with db.connection:
            playlist = utils.create_playlist(db, name)
            print(f'The playlist "{name}" has been successfully created.')

    playlist_id, author, playlist_name = playlist
    for song_name in songs:
        song = utils.choose_song(db.get_song(song_name))
        if not song:
            reply = utils.question_choice(f'The song "{song_name}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'y':
                song_id = add_song(db, song_name)
                if song_id is None:
                    continue
            else:
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
    :param name: The name of the group. Optional.
    :PRE: The database object needs to be connected.
    :POST: Asks the user of the relevant info and creates/modifies a group.
           Returns the id of the created/modified group. None if nothing was created/modified.
    """
    if not name:
        name = utils.question("Name")

    update = 'n'
    group = db.get_group(name)
    if group:
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
    :PRE: The database object needs to be connected.
    :POST: Asks the user of the relevant info and creates/modifies a album.
           Returns the id of the created/modified album. None if nothing was created.
    """
    if not name:
        name = utils.question("Name")

    group = utils.question("Group")

    update = 'n'
    group_query = db.get_group(group)
    if not group_query:
        reply = utils.question_choice(f'The group "{group}" doesn\'t. exist yet. Do you want to create it?',
                                      ['y', 'n'])
        if reply == 'y':
            group_id = add_group(db, group)
            if group_id is None:
                return None
        else:
            return None
    else:
        group_id = group_query[0]

    album = db.get_album(name, group_id)
    if album:
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
        song_query = db.get_song(song, group_id)
        if not song_query:
            reply = utils.question_choice(f'The song "{song}" doesn\'t. exist yet. Do you want to create it?',
                                          ['y', 'n'])
            if reply == 'y':
                song_id = add_song(db, song, group_id)
                if song_id is None:
                    continue
            else:
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


def list_songs(db: DBMuziek, filters: Optional[dict] = None):
    """List all songs from the database and display it on the screen with pagination.

    :author: Mathieu
    :param db: The database used.
    :param filters: The filters to apply before listing. Optional
    :PRE: The database object needs to be connected.
    :POST: Shows all the songs that match the filters.
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
    :PRE: The database object needs to be connected.
    :POST: Shows information about the group requested.
    """
    group_query = db.get_group(name, True)
    if not group_query:
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
    :PRE: The database object needs to be connected.
    :POST: Shows information about the album requested.
    """
    album_query = utils.choose_album(db.get_album(name))
    if not album_query:
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
    :PRE: The database object needs to be connected.
    :POST: Shows information about the playlist requested and creates it if needed.
    """
    playlist = db.get_playlist(name)
    if playlist is None:
        with db.connection:
            playlist = utils.create_playlist(db, name)
            print(f'The playlist "{name}" has been successfully created.')
            logger.info(f'The playlist "{name}" has been successfully created.')

    playlist_id, author, playlist_name = playlist
    utils.print_underline(f'Playlist "{playlist_name}" by [{author}] :', style='=')

    songs = db.get_playlist_songs(playlist_id)
    utils.display_songs(songs)


def list_playlists(db: DBMuziek):
    """Lists all the playlists stored.

    :param db: The database used.
    :PRE: The database object needs to be connected.
    :POST: Shows a list of all the playlists.
    """
    playlists = db.get_playlists()

    print(f"You have {len(playlists)} playlists:")

    if not playlists:
        print(" <empty>")

    for playlist in playlists:
        print(f" \"{playlist['playlist_name']}\" created by {playlist['author']}")


def download_song(db: DBMuziek, name: str, group_id: Optional[int] = None):
    """Downloads the song requested based on the url stored in the database.

    :author: Carlos
    :param db: The database used.
    :param name: Name of the song to download.
    :param group_id: Id of the group. Optional.
    :PRE: The database object needs to be connected.
    :POST: The song requested is downloaded.
    """
    downloader = SongDownloader()

    song_query = utils.choose_song(db.get_song(name, group_id))
    if not song_query:
        reply = utils.question_choice(f'The song "{name}" doesn\'t. exist yet. Do you want to create it?',
                                      ['y', 'n'])
        if reply == 'y':
            return add_song(db, name)
        else:
            return None

    print('Checking if the link is valid...')

    video_info = downloader.fetch_song(song_query["link"])
    if not video_info:
        print("No video could be found with the provided link. Modify the song entry to change it.")
        return None

    with db.connection:
        if song_query["duration"] != video_info["duration"]:
            db.update_song(song_query["song_id"], song_query["link"], song_query["genre"], video_info["duration"])

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


def download_playlist(db: DBMuziek, name: str):
    """Downloads the playlist requested based on the urls stored in the database.

    :author: Carlos
    :param db: The database used.
    :param name: Name of the playlist to download.
    :PRE: The database object needs to be connected.
    :POST: All the songs in the playlist are downloaded
    """
    playlist_query = db.get_playlist(name)
    if not playlist_query:
        print(f"The playlist {name} doesn't exist.")
        return
    songs = db.get_playlist_songs(playlist_query["playlist_id"])
    if not songs:
        print(f"The playlist {name} is empty.")
        return

    for song in songs:
        download_song(db, song["song_name"], song["group_id"])


def list_yt_playlist(db: DBMuziek, name: Optional[str] = None):
    """Lists your Youtube playlists.

    :author: Mathieu
    :param db: The database used.
    :param name: Name of the playlist. Optional.
    :PRE: The database object needs to be connected.
    :POST: Connects you to YT and lists all your existing playlists there, or the specific one if the name is provided.
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
    :param name: The Youtube playlist to import.
    :PRE: The database object needs to be connected.
    :POST: If the playlist exists on YT,
           it'll import it to the local database with the help of the user to get the information right.
    """
    if db.get_playlist(name) is not None:
        print(f'The playlist "{name}" already exists.')
        return

    yt = YoutubeAPI(db)
    playlist = yt.get_playlist(name)
    if playlist is None:
        print(f'Cannot find the playlist "{name}" on your Youtube library.')
        return

    playlist_id = utils.create_playlist(db, name)[0]
    for song in playlist.songs:
        print(f"Video Title: {song.title}")
        author, title = utils.get_info_from_title(song.title)

        print(f'Author: {author}')
        if utils.question_choice("Would you like to rename the song's author ?", ['y', 'n']) == 'y':
            author = utils.question('Author').strip()

        group_id = db.get_group(author)
        if group_id is None:
            group_id = db.create_group(author, [author])
        else:
            group_id = group_id['group_id']

        print(f'Title: {title}')
        if utils.question_choice("Would you like to rename the song's title ?", ['y', 'n']) == 'y':
            title = utils.question('Title').strip()

        song_id = db.get_song(title, group_id)
        if song_id is None:
            genre = utils.question("Song's genre").strip()
            song_id = db.create_song(title, song.url, genre, None, group_id, [])
        else:
            song_id = song_id['song_id']

        db.add_song_playlist(playlist_id, song_id)

        print("Song successfully imported.")
        logger.info(f"Added song {title} to the playlist {name} from YouTube.")

    db.commit()


def export_to_yt(db: DBMuziek, name: str):
    """Exports a playlist to Youtube.

    :author: Mathieu
    :param db: The database used.
    :param name: The playlist to export.
    :PRE: The database object needs to be connected.
    :POST: A playlist will be created in YT and the songs in the local playlist will be appended,
           if the local playlist doesn't exist the playlist will be empty.
    """
    playlist = db.get_playlist(name)
    if playlist is None:
        print(f'The playlist "{name}" does not exists.')
        return

    yt = YoutubeAPI(db)
    songs = db.get_playlist_songs(playlist['playlist_id'])

    while True:
        name = utils.question('Youtube playlist name', default=name).strip()
        playlist = yt.get_playlist(name)
        if playlist is None:
            description = utils.question('Playlist description', default='<empty>')
            if description == '<empty>':
                description = ''

            playlist = yt.create_playlist(name, description)
            break

        print('A Youtube playlist with the same name already exist.')
        if utils.question_choice("Add the songs to that playlist ?", ['y', 'n']) == 'y':
            break

    for song in songs:
        link = song['link']
        title = song['song_name']
        if link is None:
            print(f'The song "{title}" has no Youtube link.')
            link = utils.question('Give a youtube link for this song or nothing to ignore it.', default='').strip()
            if not link:
                print(f'The song "{title}" will not be added to your Youtube playlist.')
                continue

        try:
            yt.add_song(playlist, link, note=f'{song["group_name"]} - {title}')
        except ValueError:
            print(f'Unable to export the song "{title}". Reason: invalid link.')
        except RuntimeError as e:
            print(f'Unable to export the song "{title}". Reason: {e}')

    print(f'You can find the exported playlist here : https://www.youtube.com/playlist?list={playlist.id}')


def import_playlist(db: DBMuziek, name: str):
    """Imports a playlist that has been exported from this app.

    :param db: The database used.
    :param name: Name to store the playlist as.
    :PRE: The database object needs to be connected.
    :POST: If the playlist doesn't exist already, it'll be created with the exported content,
           groups and songs will be created if needed.
    """
    if db.get_playlist(name):
        print(f"The playlist {name} already exists.")
        return

    buffer = utils.question("Playlist export code")

    with db.connection:
        utils.import_playlist(db, buffer, name)

    print(f"The playlist {name} has been successfully imported.")
    logger.info(f"The playlist {name} has been successfully imported.")


def export_playlist(db: DBMuziek, name: str):
    """Exports a playlist to be imported by this app.

    :param db: The database used.
    :param name: Name of the playlist to export.
    :PRE: The database object needs to be connected.
    :POST: If the playlist exists, it'll be exported,
           the information about the songs and groups will be included as well.
    """
    playlist_query = db.get_playlist(name)
    if not playlist_query:
        print(f"The playlist {name} doesn't exist yet, create it and add songs to it.")
        return None

    playlist_songs = db.get_playlist_songs(playlist_query['playlist_id'])

    if len(playlist_songs) == 0:
        print(f"The playlist {name} is empty, nothing will be exported.")
        return None

    buffer = utils.export_playlist(db, playlist_songs, playlist_query["author"])

    print(f"Share this text to share the playlist:\n {buffer}")
    logger.info(f"The playlist {name} has been successfully exported.")


def list_groups(db: DBMuziek):
    """Lists all the existing groups in the database.

    :param db: The database used.
    :PRE: The database object needs to be connected.
    :POST: Shows a list of the existing groups.
    """
    groups = db.get_groups()

    print(f"You have {len(groups)} groups:")

    if not groups:
        print("<empty>")

    for group in groups:
        print(f"{group['group_name']}")


def list_albums(db: DBMuziek):
    """Lists all the existing albums in the database.

    :param db: The database used.
    :PRE: The database object needs to be connected.
    :POST: Shows a list of the existing albums.
    """
    albums = db.get_albums()

    print(f"You have {len(albums)} albums:")

    if not albums:
        print("<empty>")

    for album in albums:
        print(f"{album['album_name']} by {album['group_name']}")
