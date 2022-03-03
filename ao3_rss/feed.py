from distutils.log import error
import AO3
import ao3_rss.config as config
from feedgen.feed import FeedGenerator
from feedgen.feed import FeedEntry
from flask import make_response
from flask import render_template


def work_base_feed(work: AO3.Work):
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
        formatted_text = ""
        for id, text in enumerate([chapter.summary, chapter.start_notes, chapter.text, chapter.end_notes]):
            if text != "":
                if id == 0: # is summary
                    formatted_text += '<b>Summary: </b>'
                elif id == 1 or id == 3:
                    formatted_text += '<b>Notes: </b>'
                formatted_text += text + '<hr>'
        # Remove last <hr>
        entry.content(formatted_text[:-4].replace('\n', '<br><br>'), type='html')
        entries.append(entry)

    return feed, entries

def work_atom(work_id: int):
    try:
        work = AO3.Work(work_id)
    except AO3.utils.AuthError:
        return make_response(render_template("auth_required.html"), 401)
    except AO3.utils.InvalidIdError:
        return make_response(render_template("no_work.html"), 404)
    except AttributeError as e:
        error("Unknown error occurred while loading work " + str(work_id) + ": " + str(e))
        return make_response(render_template("unknown_error.html"), 500)
    if config.block_explicit_works and work.rating == 'Explicit':
        return make_response(render_template("explicit_block.html"), 403)
    feed, entries = work_base_feed(work)

    feed.id(work.url)
    feed.author({'name': work.authors[0].username})
    for entry in entries:
        entry.author({'name': work.authors[0].username})

    return feed.atom_str()

def work_rss(work_id: int):
    try:
        work = AO3.Work(work_id)
    except AO3.utils.AuthError:
        return make_response(render_template("auth_required.html"), 401)
    except AO3.utils.InvalidIdError:
        return make_response(render_template("no_work.html"), 404)
    except AttributeError as e:
        error("Unknown error occurred while loading work " + str(work_id) + ": " + str(e))
        return make_response(render_template("unknown_error.html"), 500)
    if config.block_explicit_works and work.rating == 'Explicit':
        return make_response(render_template("explicit_block.html"), 403)
    feed, entries = work_base_feed(work)

    feed.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    for entry in entries:
        entry.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})

    return feed.rss_str()

def series_base_feed(series: AO3.Series, exclude_explicit=False):
    feed = FeedGenerator()
    feed.title(series.name)
    feed.link(href=series.url, rel='alternate')
    feed.subtitle(series.description if series.description != "" else "(No description available.)")
    
    entries = []
    num_of_entries = config.number_of_works_in_feed
    work: AO3.Work
    for work in series.work_list[-num_of_entries:]:
        if config.block_explicit_works or (exclude_explicit and work.rating == 'Explicit'):
            # Note that less works will be in the feed than what is set in the config if this occurs
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

def series_atom(series_id: int, exclude_explicit=False):
    try:
        series = AO3.Series(series_id)
    except AO3.utils.AuthError:
        return make_response(render_template("auth_required.html"), 401)
    except AO3.utils.InvalidIdError:
        return make_response(render_template("no_series.html"), 404)
    except AttributeError as e:
        error("Unknown error occurred while loading series " + str(series_id) + ": " + str(e))
        return make_response(render_template("unknown_error.html"), 500)
    feed, entries = series_base_feed(series, exclude_explicit)

    feed.id(series.url)
    feed.author({'name': series.creators[0].username})
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, load=True, load_chapters=False)
        entry.author({'name': work.authors[0].username})

    return feed.atom_str()

def series_rss(series_id: int, exclude_explicit=False):
    try:
        series = AO3.Series(series_id)
    except AO3.utils.AuthError:
        return make_response(render_template("auth_required.html"), 401)
    except AO3.utils.InvalidIdError:
        return make_response(render_template("no_series.html"), 404)
    except AttributeError as e:
        error("Unknown error occurred while loading series " + str(series_id) + ": " + str(e))
        return make_response(render_template("unknown_error.html"), 500)
    feed, entries = series_base_feed(series, exclude_explicit)

    feed.author({'name': series.creators[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, load=True, load_chapters=False)
        entry.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    
    return feed.rss_str()
