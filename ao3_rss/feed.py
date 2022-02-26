import AO3
import ao3_rss.config as config
from feedgen.feed import FeedGenerator
from feedgen.feed import FeedEntry
from flask import make_response


def work_base_feed(work):
    feed = FeedGenerator()
    feed.title(work.title.replace('\uFF0C', ',')) # \uFF0C is a full-width comma
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
        for text in [chapter.summary, chapter.start_notes, chapter.text, chapter.end_notes]:
            if text != "":
                formatted_text += text + '<hr>'
        # Remove last <hr>
        entry.content(formatted_text[:-4].replace('\n', '<br><br>'), type='html')
        entries.append(entry)

    return feed, entries

def work_atom(work_id):
    try:
        work = AO3.Work(work_id)
    except AO3.utils.AuthError:
        return make_response(("Requires authentication", 401))
    except AO3.utils.InvalidIdError:
        return make_response(("No work found", 404))
    feed, entries = work_base_feed(work)

    feed.id(work.url)
    feed.author({'name': work.authors[0].username})
    for entry in entries:
        entry.author({'name': work.authors[0].username})

    return feed.atom_str()

def work_rss(work_id):
    try:
        work = AO3.Work(work_id)
    except AO3.utils.AuthError:
        return make_response(("Requires authentication", 401))
    except AO3.utils.InvalidIdError:
        return make_response(("No work found", 404))
    feed, entries = work_base_feed(work)

    feed.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    for entry in entries:
        entry.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})

    return feed.rss_str()

def series_base_feed(series):
    feed = FeedGenerator()
    feed.title(series.name)
    feed.link(href=series.url, rel='alternate')
    feed.subtitle(series.description if series.description != "" else "(No description available.)")
    
    entries = []
    num_of_entries = config.number_of_works_in_feed
    work: AO3.Work
    for work in series.work_list[-num_of_entries:]:
        entry: FeedEntry = feed.add_entry()
        entry.id(work.url)
        entry.title(work.title.replace('\uFF0C', ','))
        entry.link(href=work.url)
        entry.content(work.summary if work.summary != "" else "(No summary available.)")
        work.reload(load_chapters=False)
        # Assume UTC
        entry.published(str(work.date_published) + '+00:00')
        entry.updated(str(work.date_updated) + '+00:00')
        entries.append(entry)

    return feed, entries

def series_atom(series_id):
    try:
        series = AO3.Series(series_id)
    except AO3.utils.AuthError:
        return make_response(("Requires authentication", 401))
    except AO3.utils.InvalidIdError:
        return make_response(("No series found", 404))
    feed, entries = series_base_feed(series)

    feed.id(series.url)
    feed.author({'name': series.creators[0].username})
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, load=True, load_chapters=False)
        entry.author({'name': work.authors[0].username})

    return feed.atom_str()

def series_rss(series_id):
    try:
        series = AO3.Series(series_id)
    except AO3.utils.AuthError:
        return make_response(("Requires authentication", 401))
    except AO3.utils.InvalidIdError:
        return make_response(("No series found", 404))
    feed, entries = series_base_feed(series)

    feed.author({'name': series.creators[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    for entry in entries:
        work_id = AO3.utils.workid_from_url(entry.id())
        work = AO3.Work(work_id, load=True, load_chapters=False)
        entry.author({'name': work.authors[0].username, 'email': 'do-not-reply@archiveofourown.org'})
    
    return feed.rss_str()
