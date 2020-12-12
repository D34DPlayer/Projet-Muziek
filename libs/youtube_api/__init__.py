import logging
import re
from typing import List, Optional
from urllib.parse import urlparse

import requests

from ..database import DBMuziek
from .oauth2 import Token

logger = logging.getLogger('youtube-api')

URL_PLAYLISTS = 'https://www.googleapis.com/youtube/v3/playlists'
URL_PLAYLIST_ITEMS = 'https://www.googleapis.com/youtube/v3/playlistItems'


def parseVideoId(song: str) -> str:
    """Parse and return a valid videoId.

    :param song: The song to get the id from. Both an url to a video and its videoId are valid.
    :return: The parsed videoId.
    :raise: ValueError if the song is not valid.
    """
    url = urlparse(song)
    if url.netloc == '':
        videoId = song
    else:
        query = dict(a.split('=', 1) for a in url.query.split('&'))
        videoId = query.get('v')

        if videoId is None:
            raise ValueError(f'Invalid url: {song}')

    if re.match(r'^[0-9A-Za-z_-]{11}$', videoId) is None:
        raise ValueError(f'"{videoId}" is not a valid videoId, could it be truncated ?')

    return videoId


class PlaylistItem:
    def __init__(self, **kwargs):
        kind = kwargs.get('kind', '')
        if kind != 'youtube#playlistItem':
            raise ValueError(f"Expected kind 'youtube#playlistItem' but got {kind!r} instead.")

        self._title = kwargs['snippet']['title']
        self._id = kwargs['snippet']['resourceId']['videoId']

    def __str__(self):
        return self.title

    @property
    def id(self) -> str:
        return self._id

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/watch?v={self.id}'

    @property
    def title(self) -> str:
        return self._title


class Playlist:
    def __init__(self, token: Token, **kwargs):
        kind = kwargs.get('kind', '')
        if kind != 'youtube#playlist':
            raise ValueError(f"Expected kind 'youtube#playlist' but got {kind!r} instead.")

        self._token = token
        self._id = kwargs['id']
        self._description = kwargs['snippet']['description']
        self._author = kwargs['snippet']['channelTitle']
        self._title = kwargs['snippet']['title']
        self._songs = None

    def __str__(self):
        desc = f': {self.description}' if len(self.description) > 0 else ''
        return f'Playlist {self.title!r} by [{self.author}]{desc}'

    @property
    def id(self) -> str:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @property
    def author(self) -> str:
        return self._author

    @property
    def title(self) -> str:
        return self._title

    @property
    def songs(self) -> str:
        if self._songs is None:
            params = dict(part='snippet', playlistId=self.id, maxResults=50)
            with requests.get(URL_PLAYLIST_ITEMS, params=params, headers=self._token.headers) as r:
                data = r.json()
                self._songs = [PlaylistItem(**item) for item in data['items']]

            while data.get('nextPageToken') is not None:
                params['pageToken'] = data['nextPageToken']
                with requests.get(URL_PLAYLIST_ITEMS, params=params, headers=self._token.headers) as r:
                    data = r.json()
                    self._songs = [PlaylistItem(**item) for item in data['items']]

        return self._songs


class YoutubeAPI:
    def __init__(self, db: DBMuziek):
        self._token: Token = Token(db)
        self._playlists: List[Playlist] = None

    @property
    def playlists(self) -> List[Playlist]:
        if self._playlists is None:
            params = dict(mine=True, part='snippet')
            with requests.get(URL_PLAYLISTS, params=params, headers=self._token.headers) as r:
                data = r.json()
                self._playlists = [Playlist(self._token, **item) for item in data['items']]

            while data.get('nextPageToken') is not None:
                params['pageToken'] = data['nextPageToken']
                with requests.get(URL_PLAYLISTS, params=params, headers=self._token.headers) as r:
                    data = r.json()
                    self._playlists.extend(Playlist(self._token, **item) for item in data['items'])

        return self._playlists

    def get_playlist(self, name: str) -> Optional[Playlist]:
        """Find a playlist in your library.

        :param name: The playlist's name to find.
        :return: The playlist if found, None otherwise.
        """
        for playlist in self.playlists:
            if playlist.title.lower() == name.lower():
                return playlist

    def create_playlist(self, name: str, description: Optional[str] = None, private: bool = True) -> Playlist:
        """Create a playlist on Youtube.

        :param name: display name for the playlist.
        :param description: a description for the playlist.
        :param private: True to create a private playlist. Otherwise the playlist will be unlisted.
        :return: the freshly created playlist.
        :raise: RuntimeError if there is an error from the YoutubeAPI.
        """
        data = {
            'snippet': {
                'title': name,
                'description': description,
                'privacyStatus': ['unlisted', 'private'][private]
            }
        }
        with requests.post(URL_PLAYLISTS, json=data, params=dict(part='snippet'), headers=self._token.headers) as r:
            # fetch the playlists
            data = r.json()
            if not r.ok:
                error = data.get('error', {})
                errors = ', '.join(e.get('reason') for e in error.get('errors', []))
                raise RuntimeError(f'{error.get("code", r.status_code)}: {error.get("message", "Unknown")} - {errors}')

            playlist = Playlist(self._token, **data)
            self.playlists.append(playlist)

        return playlist

    def add_song(self, playlist: Playlist, song: str, note: str = None):
        """Add a song to a Youtube playlist.

        :param playlist: The playlist object where the song will be added.
        :param song: The song to add to the playlist. Both an url to a video and its videoId are valid.
        :raise: ValueError if the song is not valid.
        :raise: RuntimeError if there is an error from the YoutubeAPI.
        """
        data = {
            'snippet': {
                'playlistId': playlist.id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': parseVideoId(song)
                },
                'contentDetails': {
                    'note': note
                }
            }
        }
        params = dict(part='snippet')
        with requests.post(URL_PLAYLIST_ITEMS, json=data, params=params, headers=self._token.headers) as r:
            data = r.json()
            if not r.ok:
                error = data.get('error', {})
                errors = ', '.join(e.get('reason') for e in error.get('errors', []))
                raise RuntimeError(f'{error.get("code", r.status_code)}: {error.get("message", "Unknown")} - {errors}')

            if playlist._songs is not None:
                playlist._songs.append(PlaylistItem(self._token, **data))
