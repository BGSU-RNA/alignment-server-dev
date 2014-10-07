import simplejson as json

from flask import g
from flask import Flask
from flask import request
from flask import render_template

import db
import utils as ut

from flask_mime import Mime

app = Flask(__name__)
mimetype = Mime(app)


@app.before_request
def before_request():
    g.seq_db = db.rcad_connect()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'seq_db', None)
    if db is not None:
        db.close()


@mimetype('application/json')
@app.route('/', methods=['GET'])
def get_json():
    return json.dumps(ut.compute_variation(request.args))


@mimetype('text/html')
@app.route('/', methods=['GET'])
def get_html():
    if 'units' in request.args:
        return render_template('results.html',
                               **ut.compute_variation(request.args))
    pdbs = []
    # pdbs = db.list_options(g.seq_db)
    return render_template('form.html', pdbs=pdbs)


@mimetype('application/json')
@app.route('/', methods=['POST'])
def post_json():
    data = request.get_json() or request.form
    return json.dumps(ut.compute_variations(data))


@mimetype('text/html')
@app.route('/', methods=['POST'])
def post_html():
    data = request.get_json() or request.form
    return render_template('results.html',
                           **ut.compute_variation(data))


if __name__ == '__main__':
    app.run()
