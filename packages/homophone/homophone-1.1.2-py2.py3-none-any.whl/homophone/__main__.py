"""Homophone application runner"""

import configparser
import sys

import click

from functools import wraps

from click import echo, prompt

from homophone import auth
from homophone.formatter import ConsoleFormatter
from homophone.service import ServiceError, SpotifyService


HELP_OPTIONS = ["-h", "--help"]
AUTH_MESSAGE = (
    "In order to use Homophone, you must create and authorize your the "
    "application in your Spotify account. To get started, first visit "
    "https://beta.developer.spotify.com/dashboard/ and log in to your "
    "Spotify account. Then, on the developer's dashboard, click "
    '"Create a Client ID" to create a new Spotify application. '
    'Fill in anything you want on the signup form and click "Next". '
    'Select "No" when asked if you are developing a commercial '
    "integration. Then confirm that you understand the Spotify API's "
    "Terms of Service."
    "\n\n"
    "You will be given a client ID and secret for Homophone."
    "\n"
)


def authorize():
    echo(AUTH_MESSAGE)
    client_id = prompt("Please enter the client ID")
    client_secret = prompt("Please enter the client secret")
    echo("Writing client ID and secret to {}".format(auth.config_path()))
    config = configparser.ConfigParser()
    config["spotify"] = {}
    config["spotify"]["app_id"] = client_id
    config["spotify"]["secret"] = client_secret
    with open(auth.config_path(), "w") as fh:
        config.write(fh)


def save_access_token(token):
    config = configparser.ConfigParser()
    config.read(auth.config_path())
    config["spotify"]["access_token"] = token
    with open(auth.config_path(), "w") as fh:
        config.write(fh)


def ensure_auth(fn):
    @wraps(fn)
    def _ensure_auth(*args, **kwargs):
        if not auth.is_authorized():
            authorize()
        return fn(*args, **kwargs)
    return _ensure_auth


@click.command(context_settings=dict(help_option_names=HELP_OPTIONS))
@click.version_option(None, "--version", "-V", message="%(prog)s v%(version)s")
@click.option("--genre", "-g", "show_genres",
              is_flag=True, help="Show artist genres.")
@click.argument("artist")
@click.pass_context
@ensure_auth
def main(ctx, show_genres, artist):
    """Shows artists that are similar (in sound) to the given ARTIST.

    Homophone requires authorization to use the Spotify API. If you have
    not yet reqistered for authorization, Homophone will walk you
    through the steps necessary to register the application and get
    an authorization token from Spotify.

    To read more about the Spotify API, visit
    <https://developer.spotify.com/web-api/> in your browser.
    """
    app_id, secret = auth.authorization()
    svc = SpotifyService(app_id, secret, auth.access_token(), save_access_token)
    f = ConsoleFormatter(show_genres)
    lower = lambda t: t[0].lower()
    try:
        artists = svc.related_artists(artist)
    except ServiceError as e:
        echo(e.message, sys.stderr)
        ctx.exit(100)
    else:
        out = map(f, sorted(artists, key=lower))
        echo("\n".join(out))


if __name__ == "__main__": # pragma: no cover
    main()
