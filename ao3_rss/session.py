# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023 Kenneth Chew

"""
Provides tools needed to create a session with AO3.
"""
import datetime
import logging

import AO3
import requests.exceptions

from ao3_rss import config

_SESSION = None
_last_session_attempt_time = datetime.datetime.min


def get_session():
    """Returns a session with AO3. If no username and password are provided, no session is returned."""
    # pylint: disable=global-statement
    global _SESSION
    global _last_session_attempt_time
    timediff = datetime.datetime.now() - _last_session_attempt_time
    if timediff.total_seconds() > 1800 and _SESSION is None and config.USERNAME != '' and config.PASSWORD != '':
        try:
            _SESSION = AO3.Session(config.USERNAME, config.PASSWORD)
        except (TypeError, requests.exceptions.ConnectionError, requests.exceptions.SSLError):
            _last_session_attempt_time = datetime.datetime.now()
            logging.error('AO3 appears to be down. No session has been created.')
    return _SESSION
