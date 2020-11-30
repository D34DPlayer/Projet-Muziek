import logging
import os
import requests
import time
import webbrowser

from urllib.parse import urlencode

from .server import CallbackServer
from ..database import DBMuziek


logger = logging.getLogger('youtube-api')

CLIENT_ID = '910256464833-p8um3i9l37hvej73nnjr3eeeqg5q5r41.apps.googleusercontent.com'
CLIENT_SECRET = 'MGKitIbjxIFwBnuohBJoXLut'

URL_OAUTH = 'https://accounts.google.com/o/oauth2/v2/auth'
URL_REFRESH_TOKEN = 'https://oauth2.googleapis.com/token'
URL_PLAYLISTS = 'https://www.googleapis.com/youtube/v3/playlists'

REDIRECT_URI = 'http://127.0.0.1:6789/callback'

SCOPE_READONLY = 'https://www.googleapis.com/auth/youtube.readonly'
SCOPE_MODIFY = 'https://www.googleapis.com/auth/youtubepartner'


class Token:
    def __init__(self, db: DBMuziek):
        self._database = db
        self._oauth_code = db.get_setting('yt.oauth2.code')
        self._access_token = db.get_setting('yt.oauth2.access')
        self._refresh_token = db.get_setting('yt.oauth2.refresh')
        self._scope = db.get_setting('yt.oauth2.scope', '').split(',')
        self._expires_in = float(db.get_setting('yt.oauth2.expires_in', 0))
        self._expires_at = float(db.get_setting('yt.oauth2.expires_at', 0))

    def prompt_access(self, modify=False):
        scopes = [SCOPE_READONLY]
        if modify:
            scopes.append(SCOPE_MODIFY)

        state = os.urandom(16).hex()
        params = {
            'client_id': '910256464833-p8um3i9l37hvej73nnjr3eeeqg5q5r41.apps.googleusercontent.com',
            'redirect_uri': 'http://127.0.0.1:6789/callback',
            'access_type': 'offline',
            'response_type': 'code',
            'state': state,
            'scope': ','.join(scopes)
        }
        url = f'{URL_OAUTH}?{urlencode(params)}'

        logger.info(f'Opening web browser to the page: "{url}".')
        webbrowser.open_new_tab(url)

        server = CallbackServer(state)
        logger.info('Waiting for OAuth2.0 callback.')
        self._oauth_code = server.get_token()
        self._expires_at = self._expires_in = 0
        self._refresh_token = None
        self._database.set_setting('yt.oauth2.scope', ','.join(scopes))
        self._database.set_setting('yt.oauth2.code', self._oauth_code)
        self._database.set_setting('yt.oauth2.refresh', None)
        self._database.commit()
        logger.info('Got OAuth2 token.')

    def refresh(self):
        if self.needs_prompt:
            self.prompt_access()

        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': 'http://127.0.0.1:6789/callback'
        }

        if self._refresh_token is None:
            data['grant_type'] = 'authorization_code'
            data['code'] = self._oauth_code
        else:
            data['grant_type'] = 'refresh_token'
            data['refresh_token'] = self._refresh_token

        logger.info('Refreshing access token')
        with requests.post(URL_REFRESH_TOKEN, data=data) as r:
            data = r.json()
            if 'error' in data:
                logger.debug(f'Could not get a new token. Reason: {data["error"]}.')
                self.prompt_access()
                self.refresh()
                return

            self._access_token = data.get('access_token')
            self._refresh_token = data.get('refresh_token')
            self._expires_in = data.get('expires_in')
            self._expires_at = time.time() + self._expires_in

            self._database.set_setting('yt.oauth2.access', self._access_token)
            self._database.set_setting('yt.oauth2.refresh', self._refresh_token)
            self._database.set_setting('yt.oauth2.expires_at', self._expires_at)
            self._database.set_setting('yt.oauth2.expires_in', self._expires_in)
            self._database.commit()

        logger.info('Token refreshed')

    @property
    def headers(self):
        if self.needs_refresh:
            self.refresh()

        return {
            'Authorization': f'Bearer {self._access_token}',
            'Accept': 'application/json'
        }

    @property
    def needs_prompt(self) -> bool:
        return self._oauth_code is None

    @property
    def needs_refresh(self) -> bool:
        return self.needs_prompt \
            or self._access_token is None \
            or time.time() > self._expires_at - self._expires_in / 2

    @property
    def expired(self):
        return time.time() >= self._expires_at

    @property
    def can_read(self) -> bool:
        return SCOPE_READONLY in self._scope

    @property
    def can_edit(self) -> bool:
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
