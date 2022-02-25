import AO3
from feedgen.feed import FeedGenerator
from flask import make_response


def work_atom(work_id):
    try:
        work = AO3.Work(work_id)
    except AO3.utils.AuthError:
        return make_response(("Requires authentication", 401))
    except AO3.utils.InvalidIdError:
        return make_response(("No work found", 404))
    feed = FeedGenerator()
    feed.id(work.url)
    feed.title(work.title)
    feed.author({'name': work.authors[0].username, 'email': work.authors[0].username})
    feed.link(href=work.url, rel='alternate')
    feed.subtitle(work.summary)

    chapter: AO3.Chapter
    for chapter in work.chapters[-3:]:
        entry = feed.add_entry()
        entry.id(f"{work.url}/chapters/{chapter.id}")
        entry.title(f"{chapter.number}. {chapter.title}")
        entry.link(href=f"{work.url}/chapters/{chapter.id}")
        entry.author({'name': work.authors[0].username})
        formatted_text = ""
        for text in [chapter.summary, chapter.start_notes, chapter.text, chapter.end_notes]:
            if text != "":
                formatted_text += text + '<hr>'
        # Remove last <hr>
        entry.content(formatted_text[:-4].replace('\n', '<br><br>'), type='html')

    return feed.atom_str()

def series_atom(series_id):
    try:
        series = AO3.Series(series_id)
    except AO3.utils.AuthError:
        return make_response(("Requires authentication", 401))
    except AO3.utils.InvalidIdError:
        return make_response(("No work found", 404))
    feed = FeedGenerator()
    feed.id(series.url)
    feed.title(series.name)
    feed.author({'name': series.creators[0].username, 'email': series.creators[0].username})
    feed.link(href=series.url, rel='alternate')
    feed.subtitle(series.description)
    
    work: AO3.Work
    for work in series.work_list[-3:]:
        entry = feed.add_entry()
        entry.id(work.url)
        entry.title(work.title)
        entry.link(href=work.url)
        entry.author({'name': work.authors[0].username})
        entry.content(work.summary)
        work.reload(load_chapters=False)
        # Assume UTC
        entry.pubDate(str(work.date_published) + '+00:00')
        entry.updated(str(work.date_updated) + '+00:00')

    return feed.atom_str()
