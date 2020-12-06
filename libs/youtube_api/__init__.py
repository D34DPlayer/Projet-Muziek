import logging
import requests

from typing import List

from .oauth2 import Token
from ..database import DBMuziek


logger = logging.getLogger('youtube-api')

URL_PLAYLISTS = 'https://www.googleapis.com/youtube/v3/playlists'


class YoutubeAPI:
    def __init__(self, db: DBMuziek):
        self._token = Token(db)
        self._playlists = None

    @property
    def playlists(self):
        if self._playlists is None:
            with requests.get(URL_PLAYLISTS, params=dict(mine=True, part='snippet'), headers=self._token.headers) as r:
                data = r.json()
                self._playlists = data['items']
                # data['pageInfo']['totalResults']
                # data['pageInfo']['resultsPerPage']

        return self._playlists
