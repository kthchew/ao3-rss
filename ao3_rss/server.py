"""
A Flask app for serving RSS and Atom feeds for resources from Archive of Our Own (AO3).
"""
from flask import Flask
from flask import make_response
from flask import request

import ao3_rss.series
import ao3_rss.work

app = Flask(__name__)


@app.route('/works/<work_id>')
@app.route('/works/<work_id>/atom')
def work_atom(work_id):
    """Returns a response for a request for an Atom work feed."""
    resp = make_response(ao3_rss.work.atom(work_id))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/atom+xml'
    return resp


@app.route('/works/<work_id>/rss')
def work_rss(work_id):
    """Returns a response for a request for an RSS work feed."""
    resp = make_response(ao3_rss.work.rss(work_id))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/rss+xml'
    return resp


@app.route('/series/<series_id>')
@app.route('/series/<series_id>/atom')
def series_atom(series_id):
    """Returns a response for a request for an Atom series feed."""
    exclude_explicit = request.args.get('exclude_explicit') == 'true'
    resp = make_response(ao3_rss.series.atom(series_id, exclude_explicit))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/atom+xml'
    return resp


@app.route('/series/<series_id>/rss')
def series_rss(series_id):
    """Returns a response for a request for an RSS series feed."""
    exclude_explicit = request.args.get('exclude_explicit') == 'true'
    resp = make_response(ao3_rss.series.rss(series_id, exclude_explicit))
    if resp.status_code == 200:
        resp.headers['Content-Type'] = 'application/rss+xml'
    return resp
