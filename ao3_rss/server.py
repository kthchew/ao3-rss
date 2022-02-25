from flask import Flask
from flask import make_response

import ao3_rss.feed

app = Flask(__name__)


@app.route('/works/<work_id>')
def work_atom(work_id):
    resp = make_response(ao3_rss.feed.work_atom(work_id))
    resp.headers['Content-Type'] = 'application/atom+xml'
    return resp

@app.route('/series/<series_id>')
def series_atom(series_id):
    resp = make_response(ao3_rss.feed.series_atom(series_id))
    resp.headers['Content-Type'] = 'application/atom+xml'
    return resp
