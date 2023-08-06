"""Web API services"""

import base64
import requests
from functools import wraps
from requests.exceptions import HTTPError


def renew_token(fn):
    @wraps(fn)
    def _renew_token(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except HTTPError:
            self._access_token = None
            return fn(self, *args, **kwargs)
    return _renew_token


class ServiceError(Exception):
    def __init__(self, message):
        super(ServiceError, self).__init__()
        self.message = message


class UnknownArtistError(ServiceError):
    def __init__(self, artist):
        msg = "No artist like '{!s}' found".format(artist)
        super(UnknownArtistError, self).__init__(msg)


class SpotifyService:
    """Spotify web API"""

    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, app_id, secret, access_token=None, callback=None):
        """Creates a new Spotify web API object.

        'app_id' is the application ID registered with your Spotify account.
        'secret' is the client secret associated with the registered
        application.
        'access_token' is the last access_token received from the Spotify API;
        it will be renewed if necessary.
        'callback' is a function which takes one string argument representing
        a new access token. It is called whenever the access token is
        renewed.
        """
        self.app_id = app_id
        self.secret = secret
        self._callback = callback
        self._access_token = access_token

    @property
    def access_token(self):
        """Application's current access token."""
        if self._access_token:
            return self._access_token
        self._access_token = self.request_token()
        self.callback(self._access_token)
        return self._access_token

    @property
    def callback(self):
        """Called whenever the service acquires a new access token."""
        if self._callback:
            return self._callback
        return lambda *args, **kwargs: None

    @property
    def basic_auth_token(self):
        """Returns the token used for Basic authentication to the Spotify
        API. Basic auth is used when first requesting an access token. It
        is the "<app_id>:<secret>" encoded using Base 64.
        """
        s = self.app_id + ":" + self.secret
        return base64.b64encode(s.encode()).decode()

    @renew_token
    def get(self, path, *args, **kwargs):
        """Performs an HTTP GET request to the Spotify API and returns the
        result as a JSON object.
        """
        url = self.BASE_URL + path
        auth = {"Authorization": "Bearer " + self.access_token}
        hdrs = kwargs.get("headers", {})
        hdrs.update(auth)
        kwargs["headers"] = hdrs
        resp = requests.get(url, *args, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def request_token(self):
        """Requests a Spotify API access token."""
        data = {"grant_type": "client_credentials"}
        hdrs = {"Authorization": "Basic " + self.basic_auth_token}
        resp = requests.post("https://accounts.spotify.com/api/token",
                             data=data, headers=hdrs)
        resp.raise_for_status()
        return resp.json()["access_token"]

    def artist_id(self, artist):
        """Returns the Spotify ID for the given artist. If the artist cannot
        be found, an UnknownArtistError is raised.
        """
        path = "/search"
        params = {"q": artist, "type": "artist"}
        resp = self.get(path, params=params)
        try:
            return resp["artists"]["items"][0]["id"]
        except IndexError:
            raise UnknownArtistError(artist)

    def related_artists(self, artist):
        """Returns a list of artists that sound like the given artist."""
        id_ = self.artist_id(artist)
        path = "/artists/{}/related-artists".format(id_)
        resp = self.get(path)
        return list(map(lambda e: (e["name"], e["genres"]), resp["artists"]))

    def __str__(self):
        return "SpotifyService(app_id={}, secret={})".format(
            self.app_id, self.secret)
