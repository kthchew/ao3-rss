# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022 Kenneth Chew

"""
Provides methods useful for creating feeds for AO3 series.
"""
import logging
import signal

import AO3
import requests.exceptions
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator

from ao3_rss import config, session, errors

_series_requiring_auth = []


def __alarm_handler(signum, frame):
    raise TimeoutError


signal.signal(signal.SIGALRM, __alarm_handler)


def __base(series: AO3.Series, exclude_explicit=False):
    feed = FeedGenerator()
    feed.title(series.name)
    feed.link(href=series.url, rel='alternate')
    feed.subtitle(series.description if series.description != "" else "(No description available.)")

    entries = []
    num_of_entries = config.NUMBER_OF_WORKS_IN_FEED
    work: AO3.Work
    for work in series.work_list[-num_of_entries:]:
        if config.BLOCK_EXPLICIT_WORKS or (exclude_explicit and work.rating == 'Explicit'):
            # Note that fewer works will be in the feed than what is set in the config if this occurs
            continue
        entry: FeedEntry = feed.add_entry()
        entry.id(work.url)
        entry.title(work.title)
        entry.link(href=work.url)
        entry.content(work.summary if work.summary != "" else "(No summary available.)")
        if series.id in _series_requiring_auth:
            work.set_session(session.get_session())
        work.reload(load_chapters=False)
        # Assume UTC
        entry.published(str(work.date_published) + '+00:00')
        entry.updated(str(work.date_updated) + '+00:00')
        entries.append(entry)

    return feed, entries


# TODO: Refactor this mess
def __load_sync(series_id: int, use_session: bool = False):
    """Returns the AO3 series with the given `series_id`, or a Response with an error if it was unsuccessful."""
    if use_session is False and series_id in _series_requiring_auth:
        return __load_sync(series_id, True)
    sess = session.get_session() if use_session else AO3.GuestSession()
    if sess is None:
        return None, errors.AuthRequiredResponse
    try:
        series = AO3.Series(series_id, sess)
        _ = series.name  # trigger an error if the series was not loaded properly (e.g. auth required)
        return series, None
    except AO3.utils.AuthError:
        if use_session is False:
            series, err = __load_sync(series_id, True)
            if err is None:
                _series_requiring_auth.append(series_id)
        else:
            series, err = None, errors.AuthRequiredResponse
    except AO3.utils.InvalidIdError:
        series, err = None, errors.NoSuchSeriesResponse
    except AttributeError as error:
        # Generally this is because the work is not publicly available (auth required)
        if use_session is False:
            series, err = __load_sync(series_id, True)
            if err is None:
                _series_requiring_auth.append(series_id)
        else:
            logging.error("Unknown error occurred while loading series %d: %s", series_id, error)
            series, err = None, errors.UnknownErrorResponse
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError):
        series, err = None, errors.BadGatewayResponse
    return series, err


def __load(series_id: int):
    """Returns the AO3 series with the given `series_id`, or a Response with an error if it was unsuccessful."""
    signal.alarm(15)
    try:
        series, err = __load_sync(series_id, False)
    except (TimeoutError, requests.exceptions.ReadTimeout):
        return None, errors.TimeoutResponse
    signal.alarm(0)
    return series, err


def atom(series_id: int, exclude_explicit=False):
    """Returns an Atom feed for the series with the given id."""
    series, err = __load(series_id)
    if err is not None:
        return err.make_response()
    feed, entries = __base(series, exclude_explicit)

    series: AO3.Series
    feed.id(series.url)
    creator_list = ', '.join(creator.username for creator in series.creators)
    feed.author({'name': creator_list})
    sess = session.get_session() if series_id in _series_requiring_auth else AO3.GuestSession()
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, session=sess, load=True, load_chapters=False)
        author_list = ', '.join(author.username for author in work.authors)
        entry.author({'name': author_list})

    return feed.atom_str()


def rss(series_id: int, exclude_explicit=False):
    """Returns an RSS feed for the work with the given id."""
    series, err = __load(series_id)
    if err is not None:
        return err.make_response()
    feed, entries = __base(series, exclude_explicit)

    series: AO3.Series
    creator_list = ', '.join(creator.username for creator in series.creators)
    feed.author({'name': creator_list, 'email': 'do-not-reply@archiveofourown.org'})
    sess = session.get_session() if series_id in _series_requiring_auth else AO3.GuestSession()
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, session=sess, load=True, load_chapters=False)
        author_list = ', '.join(author.username for author in work.authors)
        entry.author({'name': author_list, 'email': 'do-not-reply@archiveofourown.org'})

    return feed.rss_str()
