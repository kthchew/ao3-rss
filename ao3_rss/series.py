"""
Provides methods useful for creating feeds for AO3 series.
"""
import logging

import AO3
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator
from flask import make_response, render_template

from ao3_rss import config


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
        work.reload(load_chapters=False)
        # Assume UTC
        entry.published(str(work.date_published) + '+00:00')
        entry.updated(str(work.date_updated) + '+00:00')
        entries.append(entry)

    return feed, entries


def __load(series_id: int):
    """Returns the AO3 series with the given `series_id`, or a Response with an error if it was unsuccessful."""
    try:
        return AO3.Series(series_id), None
    except AO3.utils.AuthError:
        return None, make_response(render_template("auth_required.html"), 401)
    except AO3.utils.InvalidIdError:
        return None, make_response(render_template("no_series.html"), 404)
    except AttributeError as err:
        logging.error("Unknown error occurred while loading series %d: %s", series_id, err)
        return None, make_response(render_template("unknown_error.html"), 500)


def atom(series_id: int, exclude_explicit=False):
    """Returns an Atom feed for the series with the given id."""
    series, err = __load(series_id)
    if err is not None:
        return err
    feed, entries = __base(series, exclude_explicit)

    feed.id(series.url)
    feed.author({'name': series.creators[0].username})
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, load=True, load_chapters=False)
        entry.author({'name': work.authors[0].username})

    return feed.atom_str()


def rss(series_id: int, exclude_explicit=False):
    """Returns an RSS feed for the work with the given id."""
    series, err = __load(series_id)
    if err is not None:
        return err
    feed, entries = __base(series, exclude_explicit)

    feed.author({'name': series.creators[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, load=True, load_chapters=False)
        entry.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})

    return feed.rss_str()
