import datetime
from distutils.log import error

import AO3
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator
from flask import make_response, render_template

from ao3_rss import config as config


def __base(work: AO3.Work):
    feed = FeedGenerator()
    feed.title(work.title)
    feed.link(href=work.url, rel='alternate')
    feed.subtitle(work.summary if work.summary != "" else "(No summary available.)")

    entries = []
    num_of_entries = config.number_of_chapters_in_feed
    chapter: AO3.Chapter
    for chapter in work.chapters[-num_of_entries:]:
        entry: FeedEntry = feed.add_entry()
        entry.id(f"{work.url}/chapters/{chapter.id}")
        entry.title(f"{chapter.number}. {chapter.title}")
        entry.link(href=f"{work.url}/chapters/{chapter.id}")
        if chapter.number == work.nchapters:
            entry.published(str(work.date_updated) + '+00:00')
        elif chapter.number == 1 or work.date_updated == work.date_published:
            entry.published(str(work.date_published) + '+00:00')
        else:
            # This isn't true, but it makes sure that these entries appear in the correct order when sorted by date
            # ao3-api currently does not have an easy way to check when a chapter was published
            entry.published(str(work.date_published + datetime.timedelta(seconds=chapter.number)) + '+00:00')
        formatted_text = ""
        for i, text in enumerate([chapter.summary, chapter.start_notes, chapter.text, chapter.end_notes]):
            if text != "":
                if i == 0:  # is summary
                    formatted_text += '<b>Summary: </b>'
                elif i == 1 or i == 3:
                    formatted_text += '<b>Notes: </b>'
                current_text = text.strip().replace('\n\n', '\n')  # remove unnecessary newlines
                formatted_text += current_text + '<hr>'
        # Remove last <hr>
        entry.content(formatted_text[:-4].replace('\n', '<br><br>'), type='html')
        entries.append(entry)

    return feed, entries


def __load(work_id: int):
    """Returns the AO3 work with the given `work_id`, or a Response with an error if it was unsuccessful."""
    try:
        work = AO3.Work(work_id)
    except AO3.utils.AuthError:
        return None, make_response(render_template("auth_required.html"), 401)
    except AO3.utils.InvalidIdError:
        return None, make_response(render_template("no_work.html"), 404)
    except AttributeError as e:
        error("Unknown error occurred while loading work " + str(work_id) + ": " + str(e))
        return None, make_response(render_template("unknown_error.html"), 500)
    if config.block_explicit_works and work.rating == 'Explicit':
        return None, make_response(render_template("explicit_block.html"), 403)
    else:
        return work, None


def atom(work_id: int):
    work, err = __load(work_id)
    if err is not None:
        return err
    feed, entries = __base(work)

    feed.id(work.url)
    feed.author({'name': work.authors[0].username})
    for entry in entries:
        entry.author({'name': work.authors[0].username})

    return feed.atom_str()


def rss(work_id: int):
    work, err = __load(work_id)
    if err is not None:
        return err
    feed, entries = __base(work)

    feed.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    for entry in entries:
        entry.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})

    return feed.rss_str()
