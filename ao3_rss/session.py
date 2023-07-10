# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2023 Kenneth Chew

"""
Provides tools needed to create a session with AO3.
"""
import logging

import AO3

from ao3_rss import config

_SESSION = None
if config.USERNAME != '' and config.PASSWORD != '':
    try:
        _SESSION = AO3.Session(config.USERNAME, config.PASSWORD)
    except TypeError:
        logging.error('AO3 appears to be down. No session has been created.')


def get_session():
    """Returns a session with AO3. If no username and password are provided, no session is returned."""
    return _SESSION
