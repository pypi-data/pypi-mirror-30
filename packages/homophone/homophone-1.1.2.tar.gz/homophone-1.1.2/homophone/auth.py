"""API authorization"""

import configparser
import os
import os.path


def config_path():
    """Returns the path to the config file."""
    try:
        prefix = os.environ["XDG_CONFIG_HOME"]
    except KeyError:
        prefix = os.path.expanduser("~")
        return os.path.join(prefix, ".homophone")
    else:
        return os.path.join(prefix, "homophone", "homophone.conf")


def is_authorized():
    """Returns True if the current user has already received API
    authorization.
    """
    try:
        auth = authorization()
    except KeyError:
        return False
    else:
        return auth[0] and auth[1]


def authorization():
    """Retrieves the client ID and secret."""
    config = configparser.ConfigParser()
    config.read(config_path())
    return config["spotify"]["app_id"], config["spotify"]["secret"]


def access_token():
    """Retrieves the current access token, or None if one is not saved."""
    config = configparser.ConfigParser()
    config.read(config_path())
    try:
        return config["spotify"]["access_token"]
    except KeyError:
        return None
