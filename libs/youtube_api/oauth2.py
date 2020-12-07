import logging
import os
import requests
import time
import webbrowser

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Union
from urllib.parse import urlencode, urlparse, parse_qsl

from ..database import DBMuziek


logger = logging.getLogger('youtube-api.oauth2')


CLIENT_ID = '910256464833-p8um3i9l37hvej73nnjr3eeeqg5q5r41.apps.googleusercontent.com'
CLIENT_SECRET = 'MGKitIbjxIFwBnuohBJoXLut'

URL_OAUTH = 'https://accounts.google.com/o/oauth2/v2/auth'
URL_REFRESH_TOKEN = 'https://oauth2.googleapis.com/token'
REDIRECT_URI = 'http://127.0.0.1:6789/callback'

SCOPE_READONLY = 'https://www.googleapis.com/auth/youtube.readonly'
SCOPE_MODIFY = 'https://www.googleapis.com/auth/youtubepartner'


class AuthorizationAborted(Exception):
    """Authorization aborted by the user."""


class CallbackRequest(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        query = dict(parse_qsl(url.query))

        if url.path.rstrip('/') == '/stop':
            self.reply(HTTPStatus.OK, 'bye')
            self.stop_server()
            return

        if url.path.rstrip('/') != '/callback':
            self.reply(HTTPStatus.NOT_FOUND, 'Please return to the application.')
            return

        state = query.get('state')
        if not self.server.check_state(state):
            logger.debug(f'Unexpected state: {state}')
            self.reply(HTTPStatus.INTERNAL_SERVER_ERROR, f'Unexpected state: {state}')
            return

        error = query.get('error')
        if error is not None:
            logger.debug(f'Authorization aborted. Reason: {error}')
            self.reply(HTTPStatus.OK, f'Authorization aborted. Reason: {error}')
            self.stop_server()
            return

        code = query.get('code')
        if code is None:
            logger.debug('The parameter "code" is missing.')
            self.reply(HTTPStatus.INTERNAL_SERVER_ERROR, 'The parameter "code" is missing.')
            return

        self.server.set_token(code)
        self.reply(HTTPStatus.OK, 'Your token has been saved. You can close this tab and return to the application.')
        self.stop_server()

    def reply(self, code: HTTPStatus, body: Union[str, bytes] = b''):
        if not isinstance(body, bytes):
            body = body.encode('utf-8')

        self.send_response(int(code), str(code))
        self.send_header('Connection', 'close')
        self.send_header("Content-Type", 'text/html;charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def stop_server(self):
        logger.info('Stopping server ...')
        self.wfile.flush()
        self.server.shutdown()

    def log_message(self, format, *args):
        logger.info('%s -- %s', self.address_string(), format % args)


class CallbackServer(ThreadingHTTPServer):
    def __init__(self, state, host='127.0.0.1', port=6789):
        self.__waiting_state = state
        self.__token = None
        super().__init__((host, port), CallbackRequest)

    def set_token(self, token: str):
        self.__token = token

    def check_state(self, state: str):
        return self.__waiting_state == state

    def get_token(self):
        self.serve_forever()
        if self.__token is None:
            raise AuthorizationAborted()

        return self.__token


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
