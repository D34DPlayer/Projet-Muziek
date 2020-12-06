import logging
import requests

from typing import List

from .oauth2 import Token
from ..database import DBMuziek


logger = logging.getLogger('youtube-api')

URL_PLAYLISTS = 'https://www.googleapis.com/youtube/v3/playlists'
URL_PLAYLIST_ITEMS = 'https://www.googleapis.com/youtube/v3/playlistItems'


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
                self._songs = [item for item in data['items']]

            while data.get('nextPageToken') is not None:
                params['pageToken'] = data['nextPageToken']
                with requests.get(URL_PLAYLIST_ITEMS, params=params, headers=self._token.headers) as r:
                    data = r.json()
                    self._songs = [item for item in data['items']]

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
                with requests.get(URL_PLAYLISTS, params=params, headers=self._token.header) as r:
                    data = r.json()
                    self._playlists.extend(Playlist(self._token, **item) for item in data['items'])

        return self._playlists
