import os
import simplejson as json

from flask import g
from flask import Flask
from flask import request
from flask import render_template

import db
import utils as ut
import dummy_data as dd

import mimerender

app = Flask(__name__)
mimerender = mimerender.FlaskMimeRender()

render_json = lambda template, **kwargs: json.dumps(kwargs)
render_html = lambda template, **kwargs: render_template(template, **kwargs)


@app.before_request
def before_request():
    g.rcad = None
    if not app.debug:
        g.rcad = db.rcad_connect(app.config)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'rcad', None)
    if db is not None:
        db.close()


def variations(data):
    if app.debug:
        return dd.DATA

    pdb, model, ranges = ut.ranges(data)
    known = db.list_options(g.rcad)
    ut.validate(pdb, model, ranges, known)

    def translator(chain):
        return db.get_translation(g.rcad, pdb, model, chain)

    translated = ut.translate(translator, ranges)
    return db.seqvar(g.rcad, pdb, model, translated)


def options():
    if app.debug:
        return dd.LIST_OPTIONS
    return db.list_options(g.rcad)


def structures():
    if app.debug:
        return dd.LIST_STRUCTURES
    return db.list_structures(g.rcad)


@app.route('/', methods=['GET'])
@mimerender(
    json=render_json,
    html=render_html
)
def get_html():
    if 'units' in request.args:
        full, summ, reqs = variations(request.args)
        return {'template': 'results.html', 'full': full, 'summ': summ, 'reqs': reqs}
    pdbs = options()
    mods = structures()
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
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'rb') as raw:
            config = json.load(raw)
    app.config.update(config)
    app.run()
