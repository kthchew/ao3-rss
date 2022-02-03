from flask import Flask

import ao3_rss.feed

app = Flask(__name__)


@app.route('/works/<work_id>')
def work(work_id):
    return ao3_rss.feed.for_work(work_id)
