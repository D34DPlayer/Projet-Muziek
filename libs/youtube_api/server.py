import logging

from urllib.parse import urlparse, parse_qsl
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Union


logger = logging.getLogger('youtube-api.callback-server')


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
