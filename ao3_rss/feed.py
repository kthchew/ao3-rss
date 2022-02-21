import AO3
from feedgen.feed import FeedGenerator
from flask import Response


def for_work(work_id):
    try:
        work = AO3.Work(work_id)
    except AO3.utils.AuthError:
        return Response("Requires authentication", 401)
    except AO3.utils.InvalidIdError:
        return Response("No work found", 404)
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
        formatted_text = chapter.text.replace('\n', '<br>')
        entry.content(formatted_text, type='html')

    return feed.atom_str()
