from flask import Flask

import feed

app = Flask(__name__)


@app.route('/works/<work_id>')
def work(work_id):
    return feed.for_work(work_id)
