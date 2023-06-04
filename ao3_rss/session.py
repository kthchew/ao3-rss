"""
Provides tools needed to create a session with AO3.
"""
import AO3

from ao3_rss import config

_SESSION = None
if config.USERNAME == '' or config.PASSWORD == '':
    _SESSION = AO3.GuestSession()
else:
    _SESSION = AO3.Session(config.USERNAME, config.PASSWORD)


def get_session():
    """Returns a session with AO3. If no username and password are provided, a guest session is used."""
    return _SESSION
