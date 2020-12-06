import logging
import requests

from typing import List

from .oauth2 import Token
from ..database import DBMuziek


logger = logging.getLogger('youtube-api')

URL_PLAYLISTS = 'https://www.googleapis.com/youtube/v3/playlists'


class Token:
    def __init__(self, db: DBMuziek):
        self._database = db
        self._oauth_code = db.get_setting('yt.oauth2.code')
        self._refresh_token = db.get_setting('yt.oauth2.refresh')
        self._scope = db.get_setting('yt.oauth2.scope', '').split(',')
        self._expires_in = float(db.get_setting('yt.oauth2.expires_in', 0))
        self._expires_at = float(db.get_setting('yt.oauth2.expires_at', 0))

    def prompt_access(self, modify=False):
    def needs_prompt(self) -> bool:
        return self._oauth_code is None

        return self.needs_prompt \
            or self._access_token is None \
            or time.time() > self._expires_at - self._expires_in / 2
    @property
    def can_read(self) -> bool:
        return SCOPE_MODIFY in self._scope


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
