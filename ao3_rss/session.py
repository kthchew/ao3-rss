"""
Provides tools needed to create a session with AO3.
"""
import AO3

from ao3_rss import config

_session = None


def get_session():
    """Creates a session with AO3."""
    global _session
    if _session is None:
        if config.USERNAME == '' or config.PASSWORD == '':
            _session = AO3.GuestSession()
        else:
            _session = AO3.Session(config.USERNAME, config.PASSWORD)
    return _session
