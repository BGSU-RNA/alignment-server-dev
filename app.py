import simplejson as json

from flask import g
from flask import Flask
from flask import request
from flask import Response
from flask import render_template

from flask_mime import Mime

import db
import utils as ut

app = Flask(__name__)
mimetype = Mime(app)


@app.before_request
def before_request():
    g.rcad = db.rcad_connect()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'rcad', None)
    if db is not None:
        db.close()


def variations(data):
    pdb, model, ranges = ut.ranges(data)
    known = db.list_options(g.rcad)
    ut.validate_ranges(pdb, model, ranges, known)
    return db.seqvar(g.rcad, pdb, model, ranges)


def as_json(data):
    return Response(json.dumps(variations(data)),
                    mimetype='application/json; charset=utf-8')


def as_html(data):
    return render_template('results.html', data=variations(data))


@mimetype('application/json')
@app.route('/', methods=['GET'])
def get_json():
    return as_json(request.args)


@mimetype('text/html')
@app.route('/', methods=['GET'])
def get_html():
    if 'units' in request.args:
        return as_html(request.args)
    pdbs = []
    # pdbs = db.list_options(g.rcad)
    return render_template('form.html', pdbs=pdbs)


@mimetype('application/json')
@app.route('/', methods=['POST'])
def post_json():
    data = request.get_json() or request.form
    return as_json(data)


@mimetype('text/html')
@app.route('/', methods=['POST'])
def post_html():
    data = request.get_json() or request.form
    return as_html(data)


if __name__ == '__main__':
    app.run()
