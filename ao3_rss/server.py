from flask import Flask
from flask import make_response
from flask import request

import ao3_rss.feed

app = Flask(__name__)


@app.route('/works/<work_id>')
@app.route('/works/<work_id>/atom')
def work_atom(work_id):
    resp = make_response(ao3_rss.feed.work_atom(work_id))
    resp.headers['Content-Type'] = 'application/atom+xml'
    return resp

@app.route('/works/<work_id>/rss')
def work_rss(work_id):
    resp = make_response(ao3_rss.feed.work_rss(work_id))
    resp.headers['Content-Type'] = 'application/rss+xml'
    return resp

@app.route('/series/<series_id>')
@app.route('/series/<series_id>/atom')
def series_atom(series_id):
    exclude_explicit = request.args.get('exclude_explicit') == 'true'
    resp = make_response(ao3_rss.feed.series_atom(series_id, exclude_explicit))
    resp.headers['Content-Type'] = 'application/atom+xml'
    return resp

@app.route('/series/<series_id>/rss')
def series_rss(series_id):
    exclude_explicit = request.args.get('exclude_explicit') == 'true'
    resp = make_response(ao3_rss.feed.series_rss(series_id, exclude_explicit))
    resp.headers['Content-Type'] = 'application/rss+xml'
    return resp
