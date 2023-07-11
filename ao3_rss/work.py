# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022 Kenneth Chew

"""
Provides methods useful for creating feeds for AO3 works.
"""
import datetime
import logging

from multiprocessing import Process, Queue
import AO3
import requests.exceptions
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator
from flask import make_response, render_template

from ao3_rss import config, session

_works_requiring_auth = []


def __base(work: AO3.Work):
    feed = FeedGenerator()
    feed.title(work.title)
    feed.link(href=work.url, rel='alternate')
    feed.subtitle(work.summary if work.summary != "" else "(No summary available.)")

    entries = []
    num_of_entries = config.NUMBER_OF_CHAPTERS_IN_FEED
    chapter: AO3.Chapter
    for chapter in work.chapters[-num_of_entries:]:
        entry: FeedEntry = feed.add_entry()
        entry.id(f"{work.url}/chapters/{chapter.id}")
        title = chapter.title if chapter.title else f"Chapter {chapter.number}"
        entry.title(f"{chapter.number}. {title}")
        entry.link(href=chapter.url)
        if chapter.number == work.nchapters:
            entry.published(str(work.date_updated) + '+00:00')
        elif chapter.number == 1 or work.date_updated == work.date_published:
            entry.published(str(work.date_published) + '+00:00')
        else:
            # This isn't true, but it makes sure that these entries appear in the correct order when sorted by date
            # ao3-api currently does not have an easy way to check when a chapter was published
            entry.published(str(work.date_published + datetime.timedelta(minutes=chapter.number)) + '+00:00')
        formatted_text = ""
        for i, text in enumerate([chapter.summary, chapter.start_notes, chapter.text, chapter.end_notes]):
            if text != "":
                if i == 0:  # is summary
                    formatted_text += '<b>Summary: </b>'
                elif i in (1, 3):
                    formatted_text += '<b>Notes: </b>'
                current_text = text.strip().replace('\n\n', '\n')  # remove unnecessary newlines
                formatted_text += current_text + '<hr>'
        # Remove last <hr>
        entry.content(formatted_text[:-4].replace('\n', '<br><br>'), type='html')
        entries.append(entry)

    return feed, entries


# TODO: Refactor this mess
def __load_sync(work_id: int, use_session: bool = False):
    """Returns the AO3 work with the given `work_id`, or a Response with an error if it was unsuccessful."""
    if use_session is False and work_id in _works_requiring_auth:
        return __load_sync(work_id, True)
    sess = session.get_session() if use_session else AO3.GuestSession()
    if sess is None:
        return None, make_response(render_template("auth_required.html"), 401)
    try:
        work = AO3.Work(work_id, sess)
        if config.BLOCK_EXPLICIT_WORKS and work.rating == 'Explicit':
            return None, make_response(render_template("explicit_block.html"), 403)
        return work, None
    except AO3.utils.AuthError:
        if use_session is False:
            work, err = __load_sync(work_id, True)
            if err is None:
                _works_requiring_auth.append(work_id)
        else:
            work, err = None, make_response(render_template("auth_required.html"), 401)
    except AO3.utils.InvalidIdError:
        work, err = None, make_response(render_template("no_work.html"), 404)
    except AttributeError as error:
        # Generally this is because the work is not publicly available (auth required)
        if use_session is False:
            work, err = __load_sync(work_id, True)
            if err is None:
                _works_requiring_auth.append(work_id)
        else:
            logging.error("Unknown error occurred while loading work %d: %s", work_id, error)
            work, err = None, make_response(render_template("unknown_error.html"), 500)
    except (requests.exceptions.ConnectionError, requests.exceptions.SSLError):
        work, err = None, make_response(render_template("bad_gateway.html"), 502)
    return work, err


def __load_set(work_id: int, queue: Queue):
    """Sets the queue values."""
    ret = queue.get()
    ret['work'], ret['err'] = __load_sync(work_id)
    queue.put(ret)


def __load(work_id: int):
    """Returns the AO3 work with the given `work_id`, or a Response with an error if it was unsuccessful."""
    ret = {
        'work': None,
        'err': None
    }
    queue = Queue()
    queue.put(ret)
    loader = Process(target=__load_set, args=(work_id, queue))
    loader.start()
    loader.join(15)
    if loader.is_alive():
        loader.terminate()
        return None, make_response(render_template("timeout.html"), 504)
    ret = queue.get()
    return ret['work'], ret['err']


def atom(work_id: int):
    """Returns an Atom feed for the work with the given id."""
    work, err = __load(work_id)
    if err is not None:
        return err
    feed, entries = __base(work)

    work: AO3.Work
    feed.id(work.url)
    author_list = ', '.join(author.username for author in work.authors)
    feed.author({'name': author_list})
    for entry in entries:
        entry.author({'name': author_list})

    return feed.atom_str()


def rss(work_id: int):
    """Returns an RSS feed for the work with the given id."""
    work, err = __load(work_id)
    if err is not None:
        return err
    feed, entries = __base(work)

    work: AO3.Work
    author_list = ', '.join(author.username for author in work.authors)
    feed.author({'name': author_list, 'email': 'do-not-reply@archiveofourown.org'})
    for entry in entries:
        entry.author({'name': author_list, 'email': 'do-not-reply@archiveofourown.org'})

    return feed.rss_str()
