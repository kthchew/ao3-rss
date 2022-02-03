from flask import Flask

import ao3_rss.feed

app = Flask(__name__)


@app.route('/works/<work_id>')
def work(work_id):
    resp = Flask.response_class(ao3_rss.feed.for_work(work_id))
    resp.headers['Content-Type'] = 'application/atom+xml'
    return resp
