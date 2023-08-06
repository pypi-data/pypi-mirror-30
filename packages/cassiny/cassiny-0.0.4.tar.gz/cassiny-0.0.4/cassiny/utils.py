import json
import sys
from urllib.parse import urljoin

import click
import requests
from requests.exceptions import ConnectionError

from cassiny import config


def make_no_token_request(url, method, data=None):
    """Make a request to Cassiny.io."""
    url = make_url(url)

    request_headers = {}

    if data:
        request_headers['content-type'] = 'application/json'
        data = json.dumps(data)

    with RequestContext(method=method, url=url, headers=request_headers, data=data) as response:
        return response


def make_request(
    url,
    method,
    data=None,
    headers=None,
    files=None
):
    """Make all the requests where you need a token"""
    url = make_url(url)

    request_headers = {}

    if headers:
        request_headers.update(headers)

    if data:
        request_headers['content-type'] = 'application/json'
        data = json.dumps(data)

    if files:
        data = files

    token, refresh_token = get_tokens()
    request_headers['Authorization'] = 'Bearer {}'.format(token)

    request_data = {
        "method": method,
        "url": url,
        "headers": request_headers,
        "data": data
    }

    with RequestContext(**request_data) as response:
        # Try to refresh the token and repeat the request
        if response.status_code == 401:
            new_token = refresh_auth_token(refresh_token)
            save_token(new_token, refresh_token)
            with RequestContext(**request_data) as response:
                return response
        return response


class RequestContext:
    """Context manager to catch errors."""
    def __init__(self, method, url, headers, data):
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data

    def __enter__(self):
        response = requests.request(
            self.method,
            self.url,
            headers=self.headers,
            data=self.data
        )
        if response.ok:
            return response
        else:
            try:
                print(response.json()['error'])
                sys.exit(1)
            except json.JSONDecodeError:
                print("😞....something went really bad!")
                sys.exit(1)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is ConnectionError:
            print("Impossible to connect, seems our 🚀  server is not reachable!")
            sys.exit(1)


def get_tokens():
    """Get the tokens."""
    try:
        with open(config.FOLDER, 'rb') as f:
            tokens = json.loads(f.read())
            return tokens['token'], tokens['refresh_token']
    except (KeyError, FileNotFoundError):
        click.secho(
            "You need to call `cassiny login` before running this command.", fg='red', bold=True)
        sys.exit(1)


def save_token(token, refresh_token):
    """Save the token."""
    token = {
        "token": token,
        "refresh_token": refresh_token
    }
    with open(config.FOLDER, 'wb') as f:
        f.write(json.dumps(token).encode('utf-8'))


def refresh_auth_token(refresh_token):
    """Get a new auth token."""
    with RequestContext(
        method='GET',
        url=make_url('/api/auth/refresh_token'),
        headers={'Authorization': 'Bearer {}'.format(refresh_token)}
    ) as response:
        return response.json()['token']


def make_url(url):
    """Create a valid url."""
    return urljoin(config.BASE_URI, url)
