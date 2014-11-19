import simplejson as json

from flask import g
from flask import Flask
from flask import request
from flask import render_template

import db
import utils as ut
from dummy_data import DATA

import mimerender

app = Flask(__name__)
mimerender = mimerender.FlaskMimeRender()

render_json = lambda template, **kwargs: json.dumps(kwargs)
render_html = lambda template, **kwargs: render_template(template, **kwargs)


@app.before_request
def before_request():
    g.rcad = db.rcad_connect()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'rcad', None)
    if db is not None:
        db.close()


def variations(data):
    if app.debug:
        return DATA

    pdb, model, ranges = ut.ranges(data)
    known = db.list_options(g.rcad)
    ut.validate(pdb, model, ranges, known)

    def translator(chain):
        return db.get_translation(g.rcad, pdb, model, chain)

    translated = ut.translate(translator, ranges)
    return db.seqvar(g.rcad, pdb, model, translated)


@app.route('/', methods=['GET'])
@mimerender(
    json=render_json,
    html=render_html
)
def get_html():
    if 'units' in request.args:
        return {'template': 'results.html', 'data': variations(request.args)}
    pdbs = []
    # pdbs = db.list_options(g.rcad)
    mods = []
    # mods = db.list_structures(g.rcad)
    return {'template': 'form.html', 'pdbs': pdbs, 'mods': mods}


@app.route('/', methods=['POST'])
@mimerender(
    json=render_json,
    html=render_html,
)
def post_html():
    data = request.get_json() or request.form
    return {'template': 'results.html', 'data': variations(data)}


if __name__ == '__main__':
    app.run(debug=True)
