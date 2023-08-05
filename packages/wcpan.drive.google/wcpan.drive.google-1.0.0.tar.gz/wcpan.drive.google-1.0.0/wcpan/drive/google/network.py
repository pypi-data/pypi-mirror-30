import json
import math
import random
import urllib.parse as up

from tornado import httpclient as thc, httputil as thu, gen as tg
from wcpan.logger import DEBUG, EXCEPTION, INFO, WARNING

from .util import GoogleDriveError


BACKOFF_FACTOR = 2
BACKOFF_STATUSES = ('403', '500', '502', '503', '504')


class Network(object):

    def __init__(self):
        self._access_token = None
        self._http = thc.AsyncHTTPClient()
        self._backoff_level = 0

    def set_access_token(self, token):
        self._access_token = token

    async def fetch(self, method, path, args=None, headers=None, body=None,
                    consumer=None, raise_internal_error=False):
        while True:
            await self._maybe_backoff()
            try:
                rv = await self._do_request(method, path, args, headers, body,
                                            consumer, raise_internal_error)
                return rv
            except NetworkError as e:
                if e.status != '599':
                    raise
                if e._response.raise_internal_error:
                    raise
                WARNING('wcpan.drive.google') << str(e)

    async def _do_request(self, method, path, args, headers, body, consumer,
                          raise_internal_error):
        headers = self._prepare_headers(headers)
        if args is not None:
            path = thu.url_concat(path, args)

        args = {
            'url': path,
            'method': method,
            'headers': headers,
        }
        if body is not None:
            if callable(body):
                args['body_producer'] = body
            else:
                args['body'] = body
        elif method == 'PUT':
            # for resume uploads
            args['allow_nonstandard_methods'] = True
        if consumer is not None:
            args['streaming_callback'] = consumer
        if raise_internal_error:
            # do not raise timeout from client
            args['request_timeout'] = 0.0

        request = thc.HTTPRequest(**args)
        rv = await self._http.fetch(request, raise_error=False)
        rv = Response(rv, raise_internal_error)
        rv = self._handle_status(rv)
        return rv

    def _prepare_headers(self, headers):
        h = {
            'Authorization': 'Bearer {0}'.format(self._access_token),
        }
        if headers is not None:
            h.update(headers)
        h = {k: v if isinstance(v, (bytes, str)) or v is None else str(v)
             for k, v in h.items()}
        return h

    def _handle_status(self, response):
        if backoff_needed(response):
            self._increase_backoff_level()
        else:
            self._decrease_backoff_level()

        # normal response
        if response.status[0] in ('1', '2', '3'):
            return response

        # otherwise it is an error
        raise NetworkError(response)

    def _increase_backoff_level(self):
        self._backoff_level = min(self._backoff_level + 2, 10)

    def _decrease_backoff_level(self):
        self._backoff_level = max(self._backoff_level - 1, 0)

    async def _maybe_backoff(self):
        if self._backoff_level <= 0:
            return
        seed = random.random()
        power = 2 ** self._backoff_level
        s_delay = math.floor(seed * power * BACKOFF_FACTOR)
        s_delay = min(100, s_delay)
        DEBUG('wcpan.drive.google') << 'backoff for' << s_delay
        await tg.sleep(s_delay)


class Request(object):

    def __init__(self, request):
        self._request = request

    @property
    def uri(self):
        return self._request.url

    @property
    def method(self):
        return self._request.method

    @property
    def headers(self):
        return self._request.headers


class Response(object):

    def __init__(self, response, raise_internal_error):
        self._response = response
        self._raise_internal_error = raise_internal_error
        self._request = Request(response.request)
        self._status = str(self._response.code)
        self._parsed_json = False
        self._json = None

    @property
    def status(self):
        return self._status

    @property
    def reason(self):
        return self._response.reason

    @property
    def json_(self):
        if not self._parsed_json:
            rv = self._response.body
            if not rv:
                rv = None
            else:
                rv = rv.decode('utf-8')
                try:
                    rv = json.loads(rv)
                except ValueError as e:
                    EXCEPTION('wcpan.drive.google') << rv
                    rv = None
            self._json = rv
            self._parsed_json = True
        return self._json

    @property
    def request(self):
        return self._request

    @property
    def error(self):
        return self._response.error

    @property
    def raise_internal_error(self):
        return self._raise_internal_error

    def get_header(self, key):
        h = self._response.headers.get_list(key)
        return None if not h else h[0]


class NetworkError(GoogleDriveError):

    def __init__(self, response):
        self._response = response
        self._message = '{0} {1} - {2}'.format(self.status,
                                               self._response.reason,
                                               self.json_)

    def __str__(self):
        return self._message

    @property
    def status(self):
        return self._response.status

    @property
    def fatal(self):
        return not backoff_needed(self._response)

    @property
    def json_(self):
        return self._response.json_

    @property
    def error(self):
        return self._response.error


def initialize():
    args = {
        'max_body_size': 10 * (1024 ** 3),
    }
    thc.AsyncHTTPClient.configure(None, **args)


def backoff_needed(response):
    if response.status not in BACKOFF_STATUSES:
        return False

    # if it is not a rate limit error, it could be handled immediately
    if response.status == '403':
        msg = response.json_
        if not msg:
            WARNING('wcpan.drive.google') << '403 with empty error message'
            # probably server problem, backoff for safety
            return True
        domain = msg['error']['errors'][0]['domain']
        if domain != 'usageLimits':
            return False
        INFO('wcpan.drive.google') << msg['error']['message']

    return True


initialize()
