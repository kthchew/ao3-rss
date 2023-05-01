"""
A Flask app for serving RSS and Atom feeds for resources from Archive of Our Own (AO3).
"""
from cachetools import cached, TTLCache
from flask import Flask, make_response, request, render_template
from markupsafe import escape

from ao3_rss import config
import ao3_rss.series
import ao3_rss.work

app = Flask(__name__)


@app.route('/works/<work_id>')
@app.route('/works/<work_id>/atom')
@cached(cache=TTLCache(maxsize=config.WORK_CACHE_SIZE, ttl=config.WORK_CACHE_TTL))
def work_atom(work_id):
    """Returns a response for a request for an Atom work feed."""
    try:
        work_id = int(escape(work_id))
    except ValueError:
        return make_response(render_template("no_work.html"), 404)
    resp = make_response(ao3_rss.work.atom(work_id))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/atom+xml'
    return resp


@app.route('/works/<work_id>/rss')
@cached(cache=TTLCache(maxsize=config.WORK_CACHE_SIZE, ttl=config.WORK_CACHE_TTL))
def work_rss(work_id):
    """Returns a response for a request for an RSS work feed."""
    try:
        work_id = int(escape(work_id))
    except ValueError:
        return make_response(render_template("no_work.html"), 404)
    resp = make_response(ao3_rss.work.rss(work_id))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/rss+xml'
    return resp


@app.route('/series/<series_id>')
@app.route('/series/<series_id>/atom')
@cached(cache=TTLCache(maxsize=config.SERIES_CACHE_SIZE, ttl=config.SERIES_CACHE_TTL))
def series_atom(series_id):
    """Returns a response for a request for an Atom series feed."""
    try:
        series_id = int(escape(series_id))
    except ValueError:
        return make_response(render_template("no_work.html"), 404)
    exclude_explicit = request.args.get('exclude_explicit') == 'true'
    resp = make_response(ao3_rss.series.atom(series_id, exclude_explicit))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/atom+xml'
    return resp


@app.route('/series/<series_id>/rss')
@cached(cache=TTLCache(maxsize=config.SERIES_CACHE_SIZE, ttl=config.SERIES_CACHE_TTL))
def series_rss(series_id):
    """Returns a response for a request for an RSS series feed."""
    try:
        series_id = int(escape(series_id))
    except ValueError:
        return make_response(render_template("no_work.html"), 404)
    exclude_explicit = request.args.get('exclude_explicit') == 'true'
    resp = make_response(ao3_rss.series.rss(series_id, exclude_explicit))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/rss+xml'
    return resp
